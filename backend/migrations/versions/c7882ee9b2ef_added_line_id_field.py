"""added line id field

Revision ID: c7882ee9b2ef
Revises: 6eeb6a1cc0ee
Create Date: 2021-07-28 21:39:31.265690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7882ee9b2ef'
down_revision = '6eeb6a1cc0ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('kb_c89e325f9d_uri_index', table_name='kb_c89e325f9d_namespace_binds')
    op.drop_table('kb_c89e325f9d_namespace_binds')
    op.drop_index('kb_c89e325f9d_L_c_index', table_name='kb_c89e325f9d_literal_statements')
    op.drop_index('kb_c89e325f9d_L_p_index', table_name='kb_c89e325f9d_literal_statements')
    op.drop_index('kb_c89e325f9d_L_s_index', table_name='kb_c89e325f9d_literal_statements')
    op.drop_index('kb_c89e325f9d_L_termComb_index', table_name='kb_c89e325f9d_literal_statements')
    op.drop_index('kb_c89e325f9d_literal_spoc_key', table_name='kb_c89e325f9d_literal_statements')
    op.drop_table('kb_c89e325f9d_literal_statements')
    op.drop_index('kb_c89e325f9d_T_termComb_index', table_name='kb_c89e325f9d_type_statements')
    op.drop_index('kb_c89e325f9d_c_index', table_name='kb_c89e325f9d_type_statements')
    op.drop_index('kb_c89e325f9d_klass_index', table_name='kb_c89e325f9d_type_statements')
    op.drop_index('kb_c89e325f9d_member_index', table_name='kb_c89e325f9d_type_statements')
    op.drop_index('kb_c89e325f9d_type_mkc_key', table_name='kb_c89e325f9d_type_statements')
    op.drop_table('kb_c89e325f9d_type_statements')
    op.drop_index('kb_c89e325f9d_Q_c_index', table_name='kb_c89e325f9d_quoted_statements')
    op.drop_index('kb_c89e325f9d_Q_o_index', table_name='kb_c89e325f9d_quoted_statements')
    op.drop_index('kb_c89e325f9d_Q_p_index', table_name='kb_c89e325f9d_quoted_statements')
    op.drop_index('kb_c89e325f9d_Q_s_index', table_name='kb_c89e325f9d_quoted_statements')
    op.drop_index('kb_c89e325f9d_Q_termComb_index', table_name='kb_c89e325f9d_quoted_statements')
    op.drop_index('kb_c89e325f9d_quoted_spoc_key', table_name='kb_c89e325f9d_quoted_statements')
    op.drop_table('kb_c89e325f9d_quoted_statements')
    op.drop_index('kb_c89e325f9d_A_c_index', table_name='kb_c89e325f9d_asserted_statements')
    op.drop_index('kb_c89e325f9d_A_o_index', table_name='kb_c89e325f9d_asserted_statements')
    op.drop_index('kb_c89e325f9d_A_p_index', table_name='kb_c89e325f9d_asserted_statements')
    op.drop_index('kb_c89e325f9d_A_s_index', table_name='kb_c89e325f9d_asserted_statements')
    op.drop_index('kb_c89e325f9d_A_termComb_index', table_name='kb_c89e325f9d_asserted_statements')
    op.drop_index('kb_c89e325f9d_asserted_spoc_key', table_name='kb_c89e325f9d_asserted_statements')
    op.drop_table('kb_c89e325f9d_asserted_statements')
    op.add_column('unfulfilled_messages', sa.Column('line_id', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('unfulfilled_messages', 'line_id')
    op.create_table('kb_c89e325f9d_asserted_statements',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('subject', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('predicate', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('object', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('context', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('termcomb', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='kb_c89e325f9d_asserted_statements_pkey')
    )
    op.create_index('kb_c89e325f9d_asserted_spoc_key', 'kb_c89e325f9d_asserted_statements', ['subject', 'predicate', 'object', 'context'], unique=True)
    op.create_index('kb_c89e325f9d_A_termComb_index', 'kb_c89e325f9d_asserted_statements', ['termcomb'], unique=False)
    op.create_index('kb_c89e325f9d_A_s_index', 'kb_c89e325f9d_asserted_statements', ['subject'], unique=False)
    op.create_index('kb_c89e325f9d_A_p_index', 'kb_c89e325f9d_asserted_statements', ['predicate'], unique=False)
    op.create_index('kb_c89e325f9d_A_o_index', 'kb_c89e325f9d_asserted_statements', ['object'], unique=False)
    op.create_index('kb_c89e325f9d_A_c_index', 'kb_c89e325f9d_asserted_statements', ['context'], unique=False)
    op.create_table('kb_c89e325f9d_quoted_statements',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('subject', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('predicate', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('object', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('context', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('termcomb', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('objlanguage', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('objdatatype', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='kb_c89e325f9d_quoted_statements_pkey')
    )
    op.create_index('kb_c89e325f9d_quoted_spoc_key', 'kb_c89e325f9d_quoted_statements', ['subject', 'predicate', 'object', 'objlanguage', 'context'], unique=True)
    op.create_index('kb_c89e325f9d_Q_termComb_index', 'kb_c89e325f9d_quoted_statements', ['termcomb'], unique=False)
    op.create_index('kb_c89e325f9d_Q_s_index', 'kb_c89e325f9d_quoted_statements', ['subject'], unique=False)
    op.create_index('kb_c89e325f9d_Q_p_index', 'kb_c89e325f9d_quoted_statements', ['predicate'], unique=False)
    op.create_index('kb_c89e325f9d_Q_o_index', 'kb_c89e325f9d_quoted_statements', ['object'], unique=False)
    op.create_index('kb_c89e325f9d_Q_c_index', 'kb_c89e325f9d_quoted_statements', ['context'], unique=False)
    op.create_table('kb_c89e325f9d_type_statements',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('member', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('klass', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('context', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('termcomb', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='kb_c89e325f9d_type_statements_pkey')
    )
    op.create_index('kb_c89e325f9d_type_mkc_key', 'kb_c89e325f9d_type_statements', ['member', 'klass', 'context'], unique=True)
    op.create_index('kb_c89e325f9d_member_index', 'kb_c89e325f9d_type_statements', ['member'], unique=False)
    op.create_index('kb_c89e325f9d_klass_index', 'kb_c89e325f9d_type_statements', ['klass'], unique=False)
    op.create_index('kb_c89e325f9d_c_index', 'kb_c89e325f9d_type_statements', ['context'], unique=False)
    op.create_index('kb_c89e325f9d_T_termComb_index', 'kb_c89e325f9d_type_statements', ['termcomb'], unique=False)
    op.create_table('kb_c89e325f9d_literal_statements',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('subject', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('predicate', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('object', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('context', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('termcomb', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('objlanguage', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('objdatatype', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='kb_c89e325f9d_literal_statements_pkey')
    )
    op.create_index('kb_c89e325f9d_literal_spoc_key', 'kb_c89e325f9d_literal_statements', ['subject', 'predicate', 'object', 'objlanguage', 'context'], unique=True)
    op.create_index('kb_c89e325f9d_L_termComb_index', 'kb_c89e325f9d_literal_statements', ['termcomb'], unique=False)
    op.create_index('kb_c89e325f9d_L_s_index', 'kb_c89e325f9d_literal_statements', ['subject'], unique=False)
    op.create_index('kb_c89e325f9d_L_p_index', 'kb_c89e325f9d_literal_statements', ['predicate'], unique=False)
    op.create_index('kb_c89e325f9d_L_c_index', 'kb_c89e325f9d_literal_statements', ['context'], unique=False)
    op.create_table('kb_c89e325f9d_namespace_binds',
    sa.Column('prefix', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('uri', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('prefix', name='kb_c89e325f9d_namespace_binds_pkey')
    )
    op.create_index('kb_c89e325f9d_uri_index', 'kb_c89e325f9d_namespace_binds', ['uri'], unique=False)
    # ### end Alembic commands ###