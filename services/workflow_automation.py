"""
Workflow Automation Service
Runs end-to-end processing: extract -> summarize -> translate -> speech -> email.
"""

import os
from typing import Dict, Optional


class WorkflowAutomationService:
    def __init__(self, summarizer, translator, text_to_speech, email_service, plagiarism_checker=None):
        self.summarizer = summarizer
        self.translator = translator
        self.text_to_speech = text_to_speech
        self.email_service = email_service
        self.plagiarism_checker = plagiarism_checker
        print("✅ Workflow Automation Service initialized successfully")

    def run_workflow(
        self,
        input_text: Optional[str] = None,
        file_path: Optional[str] = None,
        summary_length: str = "medium",
        summary_style: str = "paragraph",
        target_language: str = "en",
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        receiver_email: Optional[str] = None,
        subject: str = "Automated AI Content",
        run_plagiarism: bool = False,
        plagiarism_mode: str = "advanced",
    ) -> Dict:
        result = {
            "success": False,
            "steps": {
                "extract": {"status": "pending"},
                "plagiarism": {"status": "skipped"},
                "summarize": {"status": "pending"},
                "translate": {"status": "pending"},
                "speech": {"status": "pending"},
                "email": {"status": "pending"},
            },
            "outputs": {},
            "errors": [],
        }

        audio_file_path = None
        try:
            # 1) Extract/normalize input text
            try:
                text = self._get_input_text(input_text=input_text, file_path=file_path)
            except Exception as e:
                result["steps"]["extract"] = {"status": "failed", "error": str(e)}
                raise

            result["steps"]["extract"] = {
                "status": "done",
                "words": len(text.split()),
                "characters": len(text),
            }
            result["outputs"]["original_text"] = text

            # 2) Optional plagiarism check
            if run_plagiarism and self.plagiarism_checker:
                try:
                    report = self.plagiarism_checker.check_text_plagiarism(text, check_mode=plagiarism_mode)
                    result["steps"]["plagiarism"] = {"status": "done"}
                    result["outputs"]["plagiarism_report"] = report
                except Exception as e:
                    result["steps"]["plagiarism"] = {"status": "failed", "error": str(e)}
                    result["errors"].append(f"Plagiarism step failed: {e}")

            # 3) Summarize
            summary = self.summarizer.summarize(text, length=summary_length, style=summary_style)
            result["steps"]["summarize"] = {
                "status": "done",
                "summary_length": len(summary),
            }
            result["outputs"]["summary"] = summary

            # 4) Translate
            target_lang_code = self._get_iso_lang_code(target_language)
            translated_text = self.translator.translate(summary, source_lang="auto", target_lang=target_lang_code)
            result["steps"]["translate"] = {"status": "done", "target_language": target_language}
            result["outputs"]["translated_text"] = translated_text

            # 5) Convert translated text to speech
            audio_file_path = self.text_to_speech.convert_text_to_speech(
                translated_text,
                language=target_language,
                translate_before_tts=False,
            )
            result["steps"]["speech"] = {
                "status": "done",
                "audio_file": os.path.basename(audio_file_path),
            }

            # 6) Send mail with generated audio attachment
            self._validate_email_fields(sender_email, sender_password, receiver_email)
            mail_body = self._build_email_body(text, summary, translated_text, target_language, result["outputs"].get("plagiarism_report"))
            sent = self.email_service.send_email(
                sender_email=sender_email,
                sender_password=sender_password,
                receiver_email=receiver_email,
                subject=subject,
                message=mail_body,
                attachments=[audio_file_path],
            )

            if not sent:
                result["steps"]["email"] = {"status": "failed", "error": "Email delivery failed"}
                raise RuntimeError("Email delivery failed")

            result["steps"]["email"] = {"status": "done", "receiver": receiver_email}
            result["outputs"]["email_subject"] = subject
            result["success"] = True
            return result

        except Exception as e:
            result["errors"].append(str(e))
            # Mark any pending steps as not-run for clarity
            for step_name, step_info in result["steps"].items():
                if step_info.get("status") == "pending":
                    result["steps"][step_name] = {"status": "not-run"}
            return result

        finally:
            # Cleanup temp audio file after sending
            if audio_file_path and os.path.exists(audio_file_path):
                try:
                    os.unlink(audio_file_path)
                except Exception:
                    pass

    def _get_input_text(self, input_text: Optional[str], file_path: Optional[str]) -> str:
        if file_path:
            if not self.plagiarism_checker:
                raise ValueError("File extraction service unavailable")
            text = self.plagiarism_checker.extract_text_from_file(file_path)
        else:
            text = (input_text or "").strip()

        if not text:
            raise ValueError("No text content available for automation")

        if len(text.split()) < 20:
            raise ValueError("Please provide at least 20 words for meaningful automation")

        return text

    def _validate_email_fields(self, sender_email, sender_password, receiver_email):
        if not sender_email or not sender_password or not receiver_email:
            raise ValueError("sender_email, sender_password, and receiver_email are required")

    def _build_email_body(self, original_text, summary, translated_text, target_language, plagiarism_report=None):
        body_parts = [
            "Hello,",
            "",
            "This email was generated by AutoComm Workflow Automation.",
            "",
            "=== Summary ===",
            summary,
            "",
            f"=== Translated Summary ({target_language}) ===",
            translated_text,
            "",
        ]

        if plagiarism_report and plagiarism_report.get("success"):
            body_parts.extend([
                "=== Plagiarism Check ===",
                f"Score: {round(plagiarism_report.get('plagiarism_score', 0), 2)}%",
                f"Recommendation: {plagiarism_report.get('recommendation', 'N/A')}",
                "",
            ])

        body_parts.extend([
            "=== Original Text Preview ===",
            original_text[:700] + ("..." if len(original_text) > 700 else ""),
            "",
            "An MP3 attachment with spoken translated summary is included.",
            "",
            "Regards,",
            "AutoComm",
        ])

        return "\n".join(body_parts)

    def _get_iso_lang_code(self, language):
        if not language:
            return "en"
        return language.lower().split("-")[0].strip() or "en"
