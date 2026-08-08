from sarvamai import SarvamAI
from config import Config
from utils.sanitization import sanitize_model_output


_CODECS_BY_EXT = {
    ".wav": "wav",
    ".wave": "wave",
    ".mp3": "mp3",
    ".m4a": "x-m4a",
    ".mp4": "mp4",
    ".ogg": "ogg",
    ".opus": "opus",
    ".flac": "flac",
    ".aac": "aac",
    ".webm": "webm",
}


def get_client():
    return SarvamAI(api_subscription_key=Config.SARVAM_API_KEY)


def _infer_codec(filename, content_type):
    if content_type:
        mime = content_type.split(";", 1)[0].strip().lower()
        codec_from_mime = {
            "audio/webm": "webm",
            "video/webm": "webm",
            "audio/wav": "wav",
            "audio/x-wav": "x-wav",
            "audio/mpeg": "mpeg",
            "audio/mp3": "mp3",
            "audio/aac": "aac",
            "audio/ogg": "ogg",
            "audio/opus": "opus",
            "audio/flac": "flac",
            "audio/mp4": "mp4",
            "audio/x-m4a": "x-m4a",
        }
        if mime in codec_from_mime:
            return codec_from_mime[mime]

    if filename:
        lower = filename.lower()
        for ext, codec in _CODECS_BY_EXT.items():
            if lower.endswith(ext):
                return codec

    return Config.SARVAM_STT_CODEC


def transcribe_audio(audio_bytes, filename="answer.webm", content_type="audio/webm"):
    client = get_client()
    codec = _infer_codec(filename, content_type)

    response = client.speech_to_text.transcribe(
        file=(filename, audio_bytes, content_type),
        model=Config.SARVAM_STT_MODEL,
        mode="transcribe",
        language_code=Config.SARVAM_STT_LANGUAGE,
        input_audio_codec=codec,
    )

    transcript = sanitize_model_output(response.transcript)

    # Retry with automatic language detection if a strict language code yields nothing.
    if not transcript and Config.SARVAM_STT_LANGUAGE != "unknown":
        response = client.speech_to_text.transcribe(
            file=(filename, audio_bytes, content_type),
            model=Config.SARVAM_STT_MODEL,
            mode="transcribe",
            language_code="unknown",
            input_audio_codec=codec,
        )
        transcript = sanitize_model_output(response.transcript)

    return transcript