"""test example module."""
import unittest

from src.services.e2b import run_code


class TestE2B(unittest.TestCase):
    
    # @unittest.skip("Example Test Case")
    def test_run_code(self):
        # code = "import requests\nprint(requests.get('https://api.github.com').text)"
        # code = "import numpy as np\nprint(np.array([1, 2, 3]))"
        # code = "from sklearn.datasets import load_iris; from sklearn.model_selection import train_test_split; from sklearn.neighbors import KNeighborsClassifier; X, y = load_iris(return_X_y=True); X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3); model = KNeighborsClassifier(n_neighbors=3).fit(X_train, y_train); print(f'Accuracy: {model.score(X_test, y_test):.2f}')"
        code = "from langchain_community.llms import FakeListLLM; llm = FakeListLLM(responses=['This is a mock response']); print(llm.invoke('Any question'))"
        result = run_code(code)
        print(result)