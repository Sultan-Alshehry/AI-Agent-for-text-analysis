import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


# 3. Memory persistence

class TestDataManagerPersistence(unittest.TestCase):

    def setUp(self):
        import data_manager
        self.original_path = data_manager.DataManager.DATA_FILE
        self.tmp_path = Path(__file__).resolve().parent / "_test_user_data.json"
        data_manager.DataManager.DATA_FILE = self.tmp_path
        if self.tmp_path.exists():
            self.tmp_path.unlink()

    def tearDown(self):
        import data_manager
        data_manager.DataManager.DATA_FILE = self.original_path
        if self.tmp_path.exists():
            self.tmp_path.unlink()

    # saving an api key and loading it back should return the same key
    def test_api_key_save_and_load(self):
        from data_manager import DataManager
        DataManager.set_api_key("test-key-abc123-longerthan20chars")
        self.assertEqual(DataManager.get_api_key(), "test-key-abc123-longerthan20chars")

    # no key saved yet should return empty string
    def test_api_key_default_empty(self):
        from data_manager import DataManager
        self.assertEqual(DataManager.get_api_key(), "")

    # clearing the key should make it empty again
    def test_clear_api_key(self):
        from data_manager import DataManager
        DataManager.set_api_key("some-key-longerthan20chars")
        DataManager.clear_api_key()
        self.assertEqual(DataManager.get_api_key(), "")

    # mode should persist after saving
    def test_analysis_mode_save_and_load(self):
        from data_manager import DataManager
        DataManager.set_analysis_mode("genai")
        self.assertEqual(DataManager.get_analysis_mode(), "genai")
        DataManager.set_analysis_mode("berts")
        self.assertEqual(DataManager.get_analysis_mode(), "berts")

    # settings save/load and missing setting returns None
    def test_setting_save_and_load(self):
        from data_manager import DataManager
        DataManager.set_setting("theme", "dark")
        self.assertEqual(DataManager.get_setting("theme"), "dark")
        self.assertIsNone(DataManager.get_setting("nonexistent"))

    # broken json file should not crash, just return defaults
    def test_corrupted_json_returns_defaults(self):
        from data_manager import DataManager
        self.tmp_path.write_text("{invalid json!!!")
        self.assertEqual(DataManager.get_api_key(), "")

    # changing one field should not overwrite the others
    def test_data_survives_across_operations(self):
        from data_manager import DataManager
        DataManager.set_api_key("persistent-key-12345678")
        DataManager.set_analysis_mode("berts")
        DataManager.set_setting("lang", "fi")
        # check nothing got overwritten
        self.assertEqual(DataManager.get_api_key(), "persistent-key-12345678")
        self.assertEqual(DataManager.get_analysis_mode(), "berts")
        self.assertEqual(DataManager.get_setting("lang"), "fi")


# 4. Connection to AIs

class TestModeNormalization(unittest.TestCase):

    # genai and berts should normalize correctly
    def test_normalize_valid_modes(self):
        from ai_config import normalize_analysis_mode
        self.assertEqual(normalize_analysis_mode("genai"), "genai")
        self.assertEqual(normalize_analysis_mode("berts"), "berts")

    # invalid mode name should raise an error
    def test_normalize_invalid_mode(self):
        from ai_config import normalize_analysis_mode
        with self.assertRaises(ValueError):
            normalize_analysis_mode("invalid_mode")

    # check the user-facing names for each mode
    def test_display_names(self):
        from ai_config import get_mode_display_name
        self.assertEqual(get_mode_display_name("genai"), "Gemini")
        self.assertEqual(get_mode_display_name("berts"), "BERTs")


class TestAPIKeyValidation(unittest.TestCase):

    def setUp(self):
        import state, data_manager
        self._orig_key = state.API_KEY
        self._orig_path = data_manager.DataManager.DATA_FILE
        self.tmp_path = Path(__file__).resolve().parent / "_test_key_data.json"
        data_manager.DataManager.DATA_FILE = self.tmp_path

    def tearDown(self):
        import state, data_manager
        state.API_KEY = self._orig_key
        data_manager.DataManager.DATA_FILE = self._orig_path
        if self.tmp_path.exists():
            self.tmp_path.unlink()

    # a long enough key should be accepted
    def test_valid_key_accepted(self):
        from ai_config import set_gemini_api_key
        import state
        set_gemini_api_key("a" * 25)
        self.assertEqual(state.API_KEY, "a" * 25)

    # empty, whitespace-only and too short keys should be rejected
    def test_bad_keys_rejected(self):
        from ai_config import set_gemini_api_key
        with self.assertRaises(ValueError):
            set_gemini_api_key("")
        with self.assertRaises(ValueError):
            set_gemini_api_key("   ")
        with self.assertRaises(ValueError):
            set_gemini_api_key("short")


class TestModeValidationFallback(unittest.TestCase):

    def setUp(self):
        import state
        self._orig_key = state.API_KEY
        self._orig_mode = state.ANALYSIS_MODE

    def tearDown(self):
        import state
        state.API_KEY = self._orig_key
        state.ANALYSIS_MODE = self._orig_mode

    @patch("ai_config.is_keybert_available", return_value=True)
    @patch("ai_config.is_bertopic_available", return_value=True)
    
    # genai mode works when api key exists
    def test_genai_with_key(self, _b, _k):
        import state
        from ai_config import validate_and_resolve_mode
        state.API_KEY = "valid-key-1234567890"
        self.assertEqual(validate_and_resolve_mode("genai"), "genai")

    @patch("ai_config.is_keybert_available", return_value=True)
    @patch("ai_config.is_bertopic_available", return_value=True)
    
    # no api key -> should fall back to berts
    def test_genai_falls_back_to_berts_without_key(self, _b, _k):
        import state
        from ai_config import validate_and_resolve_mode
        state.API_KEY = ""
        self.assertEqual(validate_and_resolve_mode("genai"), "berts")

    @patch("ai_config.is_keybert_available", return_value=False)
    @patch("ai_config.is_bertopic_available", return_value=False)
    
    # no key and no berts deps -> should raise error
    def test_nothing_available_raises(self, _b, _k):
        import state
        from ai_config import validate_and_resolve_mode
        state.API_KEY = ""
        with self.assertRaises(EnvironmentError):
            validate_and_resolve_mode("genai")

    @patch("ai_config.is_keybert_available", return_value=False)
    @patch("ai_config.is_bertopic_available", return_value=False)
    
    # berts deps missing but key exists -> fall back to genai
    def test_berts_falls_back_to_genai_with_key(self, _b, _k):
        import state
        from ai_config import validate_and_resolve_mode
        state.API_KEY = "valid-key-1234567890"
        self.assertEqual(validate_and_resolve_mode("berts"), "genai")


class TestSetupEnvironment(unittest.TestCase):

    def setUp(self):
        import state, data_manager
        self._orig_key = state.API_KEY
        self._orig_mode = state.ANALYSIS_MODE
        self._orig_path = data_manager.DataManager.DATA_FILE
        self.tmp_path = Path(__file__).resolve().parent / "_test_setup_data.json"
        data_manager.DataManager.DATA_FILE = self.tmp_path

    def tearDown(self):
        import state, data_manager
        state.API_KEY = self._orig_key
        state.ANALYSIS_MODE = self._orig_mode
        data_manager.DataManager.DATA_FILE = self._orig_path
        if self.tmp_path.exists():
            self.tmp_path.unlink()

    # setup should load the previously saved key into state
    def test_setup_loads_saved_key(self):
        from data_manager import DataManager
        import state
        from ai_config import setup_environment
        DataManager.set_api_key("saved-key-1234567890123")
        state.API_KEY = ""
        state.ANALYSIS_MODE = ""
        setup_environment()
        self.assertEqual(state.API_KEY, "saved-key-1234567890123")

    # with a key saved, setup should pick genai mode
    def test_setup_returns_genai_when_key_set(self):
        from data_manager import DataManager
        import state
        from ai_config import setup_environment
        DataManager.set_api_key("saved-key-1234567890123")
        state.API_KEY = ""
        state.ANALYSIS_MODE = "genai"
        self.assertEqual(setup_environment(), "genai")

    # setting mode should update both state and the json file
    def test_set_mode_persists(self):
        import state
        from ai_config import set_analysis_mode
        from data_manager import DataManager
        set_analysis_mode("berts")
        self.assertEqual(state.ANALYSIS_MODE, "berts")
        self.assertEqual(DataManager.get_analysis_mode(), "berts")


class TestResponseParsing(unittest.TestCase):

    def _make_mock_response(self, text):
        mock = MagicMock()
        mock.candidates = [MagicMock()]
        mock.candidates[0].content.parts = [MagicMock()]
        mock.candidates[0].content.parts[0].text = text
        return mock

    # response wrapped in ```json ... ``` should be cleaned
    def test_strips_markdown_fences(self):
        from send_prompt_online import get_output_text
        mock = self._make_mock_response(
            '```json\n{"summary": "test", "keywords": [], "topics": []}\n```'
        )
        parsed = json.loads(get_output_text(mock))
        self.assertEqual(parsed["summary"], "test")

    # plain json without fences should also work
    def test_handles_plain_json(self):
        from send_prompt_online import get_output_text
        mock = self._make_mock_response(
            '{"summary": "hello", "keywords": ["a"], "topics": ["b"]}'
        )
        parsed = json.loads(get_output_text(mock))
        self.assertEqual(parsed["summary"], "hello")


class TestAnalyzeText(unittest.TestCase):

    def setUp(self):
        import state
        self._orig_key = state.API_KEY
        self._orig_mode = state.ANALYSIS_MODE
        state.API_KEY = "mock-key-for-testing-12345"

    def tearDown(self):
        import state
        state.API_KEY = self._orig_key
        state.ANALYSIS_MODE = self._orig_mode

    # mocked gemini call should return parsed summary and keywords
    @patch("send_prompt_online.get_output")
    def test_genai_mode_returns_parsed_result(self, mock_get_output):
        from send_prompt_online import analyze_text

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [MagicMock()]
        mock_response.candidates[0].content.parts[0].text = json.dumps({
            "summary": "A test summary",
            "keywords": ["python", "testing"],
            "topics": ["software development"],
        })
        mock_response.usage_metadata = MagicMock()
        mock_response.usage_metadata.total_token_count = 30
        mock_response.impacts = None
        mock_get_output.return_value = mock_response

        result = analyze_text("Some test text to analyze", mode="genai")
        self.assertEqual(result["summary"], "A test summary")
        self.assertIn("python", result["keywords"])
        mock_get_output.assert_called_once()

    # berts mode should use keybert+bertopic instead of gemini
    @patch("send_prompt_online.get_keybert_keywords", return_value=[("keyword1", 0.9)])
    @patch("send_prompt_online.get_bertopic_topics", return_value=[{"topic_name": "Topic A"}])
    @patch("send_prompt_online.run_with_codecarbon_tracking")
    def test_berts_mode_uses_local_models(self, mock_tracking, mock_topics, mock_keywords):
        from send_prompt_online import analyze_text
        mock_tracking.return_value = (
            ([("keyword1", 0.9)], [{"topic_name": "Topic A"}]),
            {"energy_kwh": 0.001}
        )
        result = analyze_text("Some text for local analysis", mode="berts")
        self.assertEqual(result["summary"], "")
        self.assertEqual(result["keybert_keywords"], [("keyword1", 0.9)])


if __name__ == "__main__":
    unittest.main()
