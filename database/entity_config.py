from dataclasses import dataclass
from typing import Type, Optional, List, Dict
from sqlalchemy.ext.declarative import DeclarativeMeta

from database.tables_config import (
    Publication, ArtifactPublication,
    Material, ArtifactMaterial,
    Language, ArtifactLanguage, 
    Genre, ArtifactGenre,
    ExternalResource, ArtifactExternalResource,
    Collection, ArtifactCollection
)

@dataclass
class EntityConfig:
    model_class: Type[DeclarativeMeta]
    relation_class: Type[DeclarativeMeta] 
    data_key: str
    extra_fields: Optional[List[str]] = None

ENTITY_CONFIGS: Dict[str, EntityConfig] = {
    'publications': EntityConfig(
        model_class=Publication,
        relation_class=ArtifactPublication,
        data_key='publication',
        extra_fields=['exact_reference']
    ),
    'materials': EntityConfig(
        model_class=Material,
        relation_class=ArtifactMaterial,
        data_key='material'
    ),
    'languages': EntityConfig(
        model_class=Language,
        relation_class=ArtifactLanguage,
        data_key='language'
    ),
    'genres': EntityConfig(
        model_class=Genre,
        relation_class=ArtifactGenre,
        data_key='genre',
        extra_fields=['comments']
    ),
    'external_resources': EntityConfig(
        model_class=ExternalResource,
        relation_class=ArtifactExternalResource,
        data_key='external_resource',
        extra_fields=['external_resource_key']
    ),
    'collections': EntityConfig(
        model_class=Collection,
        relation_class=ArtifactCollection,
        data_key='collection'
    )
}