import orjson
from geoalchemy2.types import _GISType
from sqlalchemy.sql import func
from geojson_pydantic import Feature, FeatureCollection, Point
from typing import Any, Callable, Optional
import orjson
from geoalchemy2.types import _GISType
from sqlalchemy.sql import func
from geojson_pydantic import Feature, FeatureCollection, Point


class GeomJSON(_GISType):
    """
    Represents a spatial data type for storing as Geometry and manipulating geometries in GeoJSON format.

    Attributes:
      name (str): The name of the spatial data type.
      from_text (str): The function used to convert a GeoJSON string to a geometry object.
      as_binary (str): The function used to convert a geometry object to a GeoJSON string.
      ElementType (Any): The type of the elements in the geometry object.
      cache_ok (bool): Indicates whether the geometry object can be cached.
    """

    name: str = "GEOMETRY"
    from_text: str = "ST_GeomFromGeoJSON"
    as_binary: str = "ST_AsGeoJSON"
    ElementType: Any = dict
    cache_ok: bool = False

    def column_expression(self, col: Any) -> Any:
        return func.ST_AsGeoJSON(col, type_=self)

    def bind_processor(self, dialect: Any) -> Callable[[Optional[Any]], str]:
        """Specific bind_processor that automatically process spatial elements."""

        if dialect.name != "postgresql":
            raise NotImplementedError("Only PostgreSQL is supported")

        return lambda geojson: orjson.dumps(geojson).decode("utf-8")

    def result_processor(
        self, dialect: Any, coltype: Any
    ) -> Callable[[Optional[str]], Any]:
        def process(value: Optional[str]) -> Any:
            if value is not None:
                return orjson.loads(value)

        return process


class Geomdantic(_GISType):
    name: str = "GEOMETRY"
    from_text: str = "ST_GeomFromGeoJSON"
    as_binary: str = "ST_AsGeoJSON"
    ElementType: Any = FeatureCollection
    cache_ok: bool = False

    def column_expression(self, col: Any) -> Any:
        return func.ST_AsGeoJSON(col, type_=self)

    def bind_processor(self, dialect: Any) -> Callable[[Optional[Any]], str]:
        """Specific bind_processor that automatically process spatial elements."""

        if dialect.name != "postgresql":
            raise NotImplementedError("Only PostgreSQL is supported")
        
        def process(value: Optional[FeatureCollection]) -> Optional[str]:
            if value is not None:
                return value.model_dump(mode='json')

        return process

    def result_processor(
        self, dialect: Any, coltype: Any
    ) -> Callable[[Optional[str]], Any]:
        def process(value: Optional[str]) -> Any:
            if value is not None:
                return FeatureCollection.model_validate_json(value)

        return process
