from typing import List, Any, Dict


class Target:
    def save(self, data: Dict[str, List[Dict]]) -> None:
        """
        Save the data to the target

        Parameters
        ----------
        data : Dict[str, List[Dict]]
            The data to save to the SQLite database
            key is the type of the resource which is transformed to a table name
            value is a list of resources which are transformed to rows
            resource is represented as a flattened dictionary where keys are columns
        """
        raise NotImplementedError("save() method not implemented")
