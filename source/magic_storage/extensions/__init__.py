from __future__ import annotations

from ._conditional import StoreIfAbsentMixin
from ._uid_proxy import UIDProxyMixin

__all__ = ["FullyFeaturedMixin", "StoreIfAbsentMixin"]


class FullyFeaturedMixin(StoreIfAbsentMixin, UIDProxyMixin):
    """Mixin class which aggregates all mixins from magic_storage.mixins
    submodule."""
