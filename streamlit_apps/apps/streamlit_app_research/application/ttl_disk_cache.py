

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

import streamlit as st
from pandas import DataFrame


class TTLDiskCache:
    """Adiciona expiração por tempo (TTL) ao cache em disco do Streamlit.

      sozinho não expira sozinho entre execuções:
    ele só recalcula quando os argumentos da função mudam. Esta classe resolve
    isso guardando um timestamp em disco (separado do cache do Streamlit) e,
    a cada chamada de .get(), comparando esse timestamp com `ttl`. Se o tempo
    estourou, o cache é limpo (.clear()) e recriado antes de retornar.

    Uso:
        cache = TTLDiskCache(name="eligible_assets", ttl=timedelta(days=1))

        @cache.wrap
        def _load(_service) -> DataFrame:
            return _service._process()

        df = cache.get(_service=service)  # recalcula só se expirou

    Atenção:
        - O timestamp de controle e o cache real do Streamlit são independentes;
          limpar um não limpa o outro automaticamente.
        - Parâmetros usados em .get() que não devem contar para o hash do
          Streamlit precisam começar com "_" (convenção do st.cache_data).
    """


    _cache_root = Path(".streamlit_cache_meta")


    def __init__(
        self,
        name: str,
        ttl: timedelta = timedelta(days=1),
        show_spinner: str | bool = True,
    ):
        self.name = name
        self.ttl = ttl
        self._timestamp_path = self._cache_root / f"{name}_last_run.txt"
        self._show_spinner = show_spinner
        self._cached_fn: Callable[..., DataFrame] | None = None


    def _is_stale(self) -> bool:
        if not self._timestamp_path.exists():
            return True
        last_run = datetime.fromisoformat(self._timestamp_path.read_text())
        return datetime.now() - last_run > self.ttl


    def _mark_fresh(self) -> None:
        self._timestamp_path.parent.mkdir(parents=True, exist_ok=True)
        self._timestamp_path.write_text(datetime.now().isoformat())


    def wrap(self, fn: Callable[..., DataFrame]) -> Callable[..., DataFrame]:
        """Use como decorator na função que produz o DataFrame."""
        cached = st.cache_data(persist="disk", show_spinner=self._show_spinner)(fn)
        self._cached_fn = cached
        return cached


    def get(self, *args, **kwargs) -> DataFrame:
        
        if self._cached_fn is None:
            raise RuntimeError(f"Nenhuma função registrada via .wrap() para '{self.name}'")


        if self._is_stale():
            self._cached_fn.clear()
            self._mark_fresh()


        return self._cached_fn(*args, **kwargs)