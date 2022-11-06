class BaseCatchAll(Exception):
    pass

class ParsingToPydanticModelException(BaseCatchAll):
    def __init__(self, data, error_trace):
        pass
    pass