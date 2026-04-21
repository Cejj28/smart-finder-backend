from whitenoise.storage import CompressedStaticFilesStorage
import logging

logger = logging.getLogger(__name__)

class SafeWhiteNoiseStorage(CompressedStaticFilesStorage):


    def compress(self, original_file):
        """
        Catches FileNotFoundError during WhiteNoise's attempt to open 
        and compress missing vendor files yielded by collectstatic finders.
        """
        try:
            yield from super().compress(original_file)
        except Exception as e:
            logger.warning(f"SafeWhiteNoiseStorage safely ignored a missing file during compression: {original_file} - {e}")
            return
