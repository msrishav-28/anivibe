"""add_vectors

Revision ID: 2026_01_25_1200
Revises: 
Create Date: 2026-01-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '2026_01_25_1200'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable vector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add columns
    op.add_column('anime', sa.Column('embedding_clip', Vector(512), nullable=True))
    op.add_column('anime', sa.Column('embedding_sbert', Vector(384), nullable=True))

    # Create match function for Supabase (RPC)
    op.execute("""
    create or replace function match_anime_embeddings (
      query_embedding vector(512),
      match_threshold float,
      match_count int
    )
    returns table (
      id int,
      title text,
      similarity float
    )
    language plpgsql
    as $$
    begin
      return query
      select
        anime.id,
        anime.title,
        1 - (anime.embedding_clip <=> query_embedding) as similarity
      from anime
      where 1 - (anime.embedding_clip <=> query_embedding) > match_threshold
      order by anime.embedding_clip <=> query_embedding
      limit match_count;
    end;
    $$;
    """)
    
    # Create match function for SBERT (RPC)
    op.execute("""
    create or replace function match_anime_text_embeddings (
      query_embedding vector(384),
      match_threshold float,
      match_count int
    )
    returns table (
      id int,
      title text,
      similarity float
    )
    language plpgsql
    as $$
    begin
      return query
      select
        anime.id,
        anime.title,
        1 - (anime.embedding_sbert <=> query_embedding) as similarity
      from anime
      where 1 - (anime.embedding_sbert <=> query_embedding) > match_threshold
      order by anime.embedding_sbert <=> query_embedding
      limit match_count;
    end;
    $$;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS match_anime_text_embeddings")
    op.execute("DROP FUNCTION IF EXISTS match_anime_embeddings")
    op.drop_column('anime', 'embedding_sbert')
    op.drop_column('anime', 'embedding_clip')
