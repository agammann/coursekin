import json
import unittest
from coursekin.provider import validate_answer, ProviderError


class SourceReferences(unittest.TestCase):
    def test_known_citations_and_missing_inline_fallback(self):
        value = json.dumps({'answer': 'The final is 40 percent [2].', 'sourceNumbers': [2]})
        self.assertEqual(validate_answer(value, [1, 2]), 'The final is 40 percent [2].')
        value = json.dumps({'answer': 'The final is 40 percent.', 'sourceNumbers': [2, 2]})
        self.assertEqual(validate_answer(value, [1, 2]), 'The final is 40 percent.\n\nSource excerpts: [2]')

    def test_invalid_or_unlisted_citations_and_secret_are_rejected(self):
        cases = [
            {'answer': 'Policy [99].', 'sourceNumbers': [99]},
            {'answer': 'Policy [2].', 'sourceNumbers': [1]},
            {'answer': 'Policy.', 'sourceNumbers': [True]},
            {'answer': 'Policy.', 'sourceNumbers': []},
            {'answer': 'private-marker', 'sourceNumbers': [1]},
        ]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ProviderError):
                validate_answer(json.dumps(value), [1, 2], 'private-marker')
        with self.assertRaises(ProviderError):
            validate_answer('not JSON', [1])
