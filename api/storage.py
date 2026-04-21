import logging
from whitenoise.storage import CompressedStaticFilesStorage

logger = logging.getLogger(__name__)


class SafeWhiteNoiseStorage(CompressedStaticFilesStorage):
    """
    A custom WhiteNoise storage backend that silently skips any files that
    cannot be found during compression (e.g. missing Django admin SVG icons
    referenced in base.css that no longer exist in the installed package).
    This prevents the build from crashing on Render while still compressing
    all other static files correctly.

    Cloudinary media storage is unaffected — this only applies to static files.
    """

    def _compress_path(self, path):
        """
        Override WhiteNoise's internal _compress_path so that if a file
        referenced in a CSS/JS cannot be opened (FileNotFoundError), we
        silently skip it instead of crashing collectstatic.
        """
        try:
            yield from super()._compress_path(path)
        except FileNotFoundError as e:
            logger.warning(
                "SafeWhiteNoiseStorage: skipping missing file during "
                f"compression (this is safe to ignore): {path} — {e}"
            )
            return
