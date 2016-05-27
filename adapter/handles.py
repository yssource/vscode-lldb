from typing import Dict, Any

class Handles:
    def __init__(self): # type: (Handles) -> None
        self.dict = {} # type: Dict[int, Any]
        self.next_handle = 1000

    def create(self, value): # type: (Handles, Any) -> int
        h = self.next_handle
        self.dict[h] = value
        self.next_handle += 1
        return h

    def get(self, handle, dflt=None): # type: (Handles, int, Any) -> Any
        return self.dict.get(handle, dflt)

    def reset(self): # type: (Handles) -> None
        self.dict.clear()
