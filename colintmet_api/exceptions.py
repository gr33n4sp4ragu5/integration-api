class FilteringByDateException(Exception):
    def __init__(self, message="You must especify both start and end time if you want to filter by time"):
        self.message = message
        super().__init__(self.message)
