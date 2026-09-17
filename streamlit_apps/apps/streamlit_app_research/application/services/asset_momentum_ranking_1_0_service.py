from __future__ import annotations

from datetime import timedelta

import numpy as np
from pandas import DataFrame, concat
from sklearn.base import clone
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from streamlit_apps.apps.streamlit_app_research.application.services.asset_price_service import (
    AssetPriceService,
)
from streamlit_apps.apps.streamlit_app_research.application.ttl_disk_cache import (
    TTLDiskCache,
)


class AssetMomentumRankingService:
    """Gera um ranking relativo de momentum para um universo de ativos.

    O Ridge e treinado com observacoes historicas de todos os tickers, mas as
    janelas de retorno e volatilidade sao calculadas separadamente por ativo.
    O resultado e o ranking da ultima data disponivel, pronto para exibicao.
    """


    FEATURE_WINDOWS = (5, 10, 20)
    HORIZON = 5
    N_FOLDS = 5
    TEST_BLOCK_DAYS = 252
    MIN_TRAIN_DAYS = 756


    def __init__(self) -> None:
        self.asset_price_service = AssetPriceService()


    @staticmethod
    def _forward_cumulative_return(ret, horizon: int):
        log_returns = np.log1p(ret)
        return np.expm1(log_returns.rolling(horizon).sum().shift(-horizon))


    @staticmethod
    def _trailing_cumulative_return(ret, window: int):
        return np.expm1(np.log1p(ret).rolling(window).sum())


    @staticmethod
    def _trailing_volatility(ret, window: int):
        return ret.rolling(window).std()


    def _get_returns(self, tickers: tuple[str, ...], period: str) -> DataFrame:
        returns_by_ticker = []

        for ticker in tickers:
            price = self.asset_price_service.get_asset_price(
                tickers=ticker,
                period=period,
                interval="1d",
            )
            returns_by_ticker.append(
                price.set_index("Date")["Adj Close"].pct_change().rename(ticker)
            )

        return concat(returns_by_ticker, axis=1).sort_index()


    def _build_dataset(self, tickers: tuple[str, ...], period: str) -> tuple[DataFrame, list[str]]:
        returns = self._get_returns(tickers, period)
        long_df = (
            returns.reset_index()
            .melt(id_vars="Date", var_name="ticker", value_name="ret")
            .rename(columns={"Date": "date"})
            .sort_values(["ticker", "date"])
            .reset_index(drop=True)
        )

        grouped_returns = long_df.groupby("ticker")["ret"]
        long_df["fwd_ret_5d"] = grouped_returns.transform(
            self._forward_cumulative_return,
            self.HORIZON,
        )
        long_df["target"] = long_df["fwd_ret_5d"] - long_df.groupby("date")[
            "fwd_ret_5d"
        ].transform("mean")

        for window in self.FEATURE_WINDOWS:
            long_df[f"mom_{window}d"] = grouped_returns.transform(
                self._trailing_cumulative_return,
                window,
            )
            long_df[f"vol_{window}d"] = grouped_returns.transform(
                self._trailing_volatility,
                window,
            )

        long_df["ret_vs_mkt"] = long_df["ret"] - long_df.groupby("date")[
            "ret"
        ].transform("mean")

        for window in self.FEATURE_WINDOWS:
            long_df[f"mom_{window}d_vs_mkt"] = long_df[f"mom_{window}d"] - long_df.groupby(
                "date"
            )[f"mom_{window}d"].transform("mean")

        feature_columns = [
            column
            for column in long_df.columns
            if column.startswith(("mom_", "vol_")) or column == "ret_vs_mkt"
        ]
        return long_df, feature_columns


    def _get_walk_forward_metrics(
        self,
        train_df: DataFrame,
        feature_columns: list[str],
    ) -> dict[str, float | int]:
        dates = np.array(sorted(train_df["date"].unique()))
        first_test_start = max(
            self.MIN_TRAIN_DAYS,
            len(dates) - self.N_FOLDS * self.TEST_BLOCK_DAYS,
        )
        fold_starts = list(
            range(first_test_start, len(dates), self.TEST_BLOCK_DAYS)
        )[:self.N_FOLDS]
        predictions = []
        model_template = make_pipeline(StandardScaler(), Ridge(alpha=10.0))

        for test_start_idx in fold_starts:
            test_end_idx = min(test_start_idx + self.TEST_BLOCK_DAYS, len(dates))
            train_end_idx = test_start_idx - self.HORIZON - 1
            if train_end_idx <= 0 or test_start_idx >= test_end_idx:
                continue

            fit_data = train_df[train_df["date"].isin(dates[:train_end_idx])]
            test_data = train_df[
                train_df["date"].isin(dates[test_start_idx:test_end_idx])
            ].copy()

            fold_model = clone(model_template)
            fold_model.fit(fit_data[feature_columns], fit_data["target"])
            test_data["ridge_score"] = fold_model.predict(test_data[feature_columns])
            predictions.append(test_data)

        if not predictions:
            raise ValueError("Historico insuficiente para validar o ranking fora da amostra.")

        prediction_df = concat(predictions, ignore_index=True)
        top_picks = prediction_df.loc[
            prediction_df["ridge_score"]
            == prediction_df.groupby("date")["ridge_score"].transform("max")
        ]
        return {
            "ridge_hit_rate_walk_forward": float(top_picks["target"].gt(0).mean()),
            "test_days": int(top_picks["date"].nunique()),
            "folds": len(predictions),
        }


    def _process(self, tickers: tuple[str, ...], period: str) -> dict[str, object]:
        long_df, feature_columns = self._build_dataset(tickers, period)
        train_df = long_df.dropna(subset=feature_columns + ["target"])
        live_date = long_df["date"].max()
        live_df = long_df.loc[long_df["date"] == live_date].dropna(
            subset=feature_columns
        ).copy()

        if train_df.empty or live_df.empty:
            raise ValueError("Historico insuficiente para gerar o ranking de momentum.")

        model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
        model.fit(train_df[feature_columns], train_df["target"])
        live_df["ridge_score"] = model.predict(live_df[feature_columns])

        ranking = (
            live_df.sort_values("ridge_score", ascending=False)[
                ["date", "ticker", "ridge_score", "mom_5d", "vol_5d", "mom_5d_vs_mkt"]
            ]
            .rename(columns={"mom_5d_vs_mkt": "mom_5d_vs_universo"})
            .reset_index(drop=True)
        )
        return {
            "ranking": ranking,
            "metrics": self._get_walk_forward_metrics(train_df, feature_columns),
        }


_ranking_cache = TTLDiskCache(
    name="asset_momentum_ranking",
    ttl=timedelta(minutes=5),
    show_spinner="Calculando ranking de momentum...",
)


@_ranking_cache.wrap
def _get_current_ranking_cached(
    _service: AssetMomentumRankingService,
    tickers: tuple[str, ...],
    period: str,
) -> dict[str, object]:
    return _service._process(tickers, period)


def get_current_momentum_ranking(
    service: AssetMomentumRankingService,
    tickers: list[str],
    period: str = "10y",
) -> dict[str, object]:
    """Retorna o ranking atual e as métricas walk-forward do Ridge."""
    normalized_tickers = tuple(sorted(set(tickers)))
    if len(normalized_tickers) < 2:
        raise ValueError("O ranking requer ao menos dois ativos no universo.")

    return _ranking_cache.get(
        _service=service,
        tickers=normalized_tickers,
        period=period,
    )
