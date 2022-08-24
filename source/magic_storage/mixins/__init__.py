from __future__ import annotations

from ._conditional import CacheIfMissingMixin

__all__ = ["FullyFeaturedMixin", "CacheIfMissingMixin"]


class FullyFeaturedMixin(CacheIfMissingMixin):
    """Mixin class which aggregates all mixins from magic_storage.mixins
    submodule."""
