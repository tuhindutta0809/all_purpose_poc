import re
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Parenthesis
from sqlparse.tokens import Keyword, DML
def extract_subqueries(parsed):
   """Extract subqueries and their aliases from parsed SQL."""
   subqueries = []
   from_seen = False
   for token in parsed.tokens:
       if from_seen:
           if isinstance(token, Parenthesis):
               # Extract subquery content
               subquery = token.value.strip(' \n()')
               # Look ahead for alias
               next_token = parsed.token_next(token)
               if next_token and next_token.value.upper() == 'AS':
                   alias_token = parsed.token_next(next_token)
                   if alias_token:
                       alias = alias_token.value.strip()
                       subqueries.append((subquery, alias))
           from_seen = False
       if token.ttype is Keyword and token.value.upper() in ('FROM', 'JOIN'):
           from_seen = True
   return subqueries
def convert_to_cte(sql):
   parsed = sqlparse.parse(sql)[0]
   subqueries = extract_subqueries(parsed)
   # Build CTE clauses and replacement map
   ctes = []
   replacements = []
   for idx, (subquery, alias) in enumerate(subqueries):
       cte_name = alias or f'cte_{idx+1}'
       ctes.append(f"{cte_name} AS (\n{subquery}\n)")
       replacements.append((re.escape(f'({subquery}) AS {alias}'), cte_name))
   # Replace subqueries with CTE names in the original SQL
   modified_sql = sql
   for old, new in replacements:
       modified_sql = re.sub(old, new, modified_sql, flags=re.IGNORECASE | re.DOTALL)
   # Add WITH clause if CTEs exist
   if ctes:
       modified_sql = f'WITH {", ".join(ctes)}\n{modified_sql}'
   return modified_sql
# Example usage
original_sql = """
SELECT a, b FROM (
   SELECT x AS a FROM table1
) AS sub1 JOIN (
   SELECT y AS b FROM table2
) AS sub2 ON sub1.a = sub2.b;
"""
converted_sql = convert_to_cte(original_sql)
print(converted_sql)