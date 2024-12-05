from dataclasses import dataclass
from typing import Type, Optional, List, Dict
from sqlalchemy.ext.declarative import DeclarativeMeta

from database.cdli_tables_config import (
    CDLIPublication, CDLIArtifactPublication,
    CDLIMaterial, CDLIArtifactMaterial,
    CDLILanguage, CDLIArtifactLanguage, 
    CDLIGenre, CDLIArtifactGenre,
    CDLIExternalResource, CDLIArtifactExternalResource,
    CDLICollection, CDLIArtifactCollection
)

@dataclass
class EntityConfig:
    model_class: Type[DeclarativeMeta]
    relation_class: Type[DeclarativeMeta] 
    data_key: str
    extra_fields: Optional[List[str]] = None

ENTITY_CONFIGS: Dict[str, EntityConfig] = {
    'publications': EntityConfig( # publications is the outer key in the JSON file
        model_class=CDLIPublication, # The main table class. Here, it stores basic publication info
        relation_class=CDLIArtifactPublication, # The association table class. Here, it links publications to artifacts
        data_key='publication', # Inner key in the JSON
        extra_fields=['exact_reference'] # additional fields to copy
    ),
    'materials': EntityConfig(
        model_class=CDLIMaterial,
        relation_class=CDLIArtifactMaterial,
        data_key='material'
    ),
    'languages': EntityConfig(
        model_class=CDLILanguage,
        relation_class=CDLIArtifactLanguage,
        data_key='language'
    ),
    'genres': EntityConfig(
        model_class=CDLIGenre,
        relation_class=CDLIArtifactGenre,
        data_key='genre',
        extra_fields=['comments']
    ),
    'external_resources': EntityConfig(
        model_class=CDLIExternalResource,
        relation_class=CDLIArtifactExternalResource,
        data_key='external_resource',
        extra_fields=['external_resource_key']
    ),
    'collections': EntityConfig(
        model_class=CDLICollection,
        relation_class=CDLIArtifactCollection,
        data_key='collection'
    )
}