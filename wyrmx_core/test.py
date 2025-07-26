from wyrmx_core.app import WyrmxAPP
from fastapi.testclient import TestClient



class WyrmxTestClient(TestClient):

    def __init__(self, app: WyrmxAPP):
        super().__init__(app)

