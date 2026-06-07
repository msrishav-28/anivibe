"""add_rls_policies

Revision ID: 1003aaf9cabb
Revises: 2026_01_25_1200
Create Date: 2026-01-25 07:46:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1003aaf9cabb'
down_revision = '2026_01_25_1200'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enable RLS
    op.execute("ALTER TABLE profiles ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE watchlist_entries ENABLE ROW LEVEL SECURITY")

    # 2. Profiles Policies
    # Public read access
    op.execute("""
        CREATE POLICY "Public profiles are viewable by everyone"
        ON profiles FOR SELECT
        USING ( true );
    """)
    # User can insert their own profile
    op.execute("""
        CREATE POLICY "Users can insert their own profile"
        ON profiles FOR INSERT
        WITH CHECK ( auth.uid() = id );
    """)
    # User can update their own profile
    op.execute("""
        CREATE POLICY "Users can update own profile"
        ON profiles FOR UPDATE
        USING ( auth.uid() = id );
    """)

    # 3. Watchlist Policies
    # Public read access (assuming watchlists are public by default for social)
    op.execute("""
        CREATE POLICY "Watchlists are viewable by everyone"
        ON watchlist_entries FOR SELECT
        USING ( true );
    """)
    # CRUD for owner
    op.execute("""
        CREATE POLICY "Users can insert their own watchlist entries"
        ON watchlist_entries FOR INSERT
        WITH CHECK ( auth.uid() = user_id );
    """)
    op.execute("""
        CREATE POLICY "Users can update their own watchlist entries"
        ON watchlist_entries FOR UPDATE
        USING ( auth.uid() = user_id );
    """)
    op.execute("""
        CREATE POLICY "Users can delete their own watchlist entries"
        ON watchlist_entries FOR DELETE
        USING ( auth.uid() = user_id );
    """)


def downgrade() -> None:
    # Drop Policies
    op.execute("DROP POLICY IF EXISTS \"Public profiles are viewable by everyone\" ON profiles")
    op.execute("DROP POLICY IF EXISTS \"Users can insert their own profile\" ON profiles")
    op.execute("DROP POLICY IF EXISTS \"Users can update own profile\" ON profiles")
    
    op.execute("DROP POLICY IF EXISTS \"Watchlists are viewable by everyone\" ON watchlist_entries")
    op.execute("DROP POLICY IF EXISTS \"Users can insert their own watchlist entries\" ON watchlist_entries")
    op.execute("DROP POLICY IF EXISTS \"Users can update their own watchlist entries\" ON watchlist_entries")
    op.execute("DROP POLICY IF EXISTS \"Users can delete their own watchlist entries\" ON watchlist_entries")

    # Disable RLS
    op.execute("ALTER TABLE profiles DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE watchlist_entries DISABLE ROW LEVEL SECURITY")
