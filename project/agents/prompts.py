###################
# Schema Template #
###################

SCHEMA = lambda nodes, relations, connections: f"""
List of nodes in the form of (:Node) property1: TYPE, property2: TYPE, ...:
{"\n".join(nodes)}

List of relations in the form of (:Relation) property1: TYPE, property2: TYPE, ...:
{"\n".join(relations)}

How the nodes are connected (use ONLY these connections):
{connections}
"""


##############################
# Prompts for GuardrailsStep #
##############################

GUARDRAILS_SYSTEM = """
Given a user question and a graph database schema you need to answer if the question can be answered with the database described in the schema provided.
To do that, find the core entities described in the question and see if there is a node in the schema for that.
If the question is related to the graph database, output "yes". Otherwise, output "no".
"""

GUARDRAILS_USER = lambda question, schema: f"""
Can the following question be answered using the graph database based on the schema provided?
Answer with only "yes" or "no", nothing else.

Question: {question}

Schema:
{schema}
"""

############################
# Prompts for GenQueryStep #
############################

GEN_QUERY_SYSTEM = """
Given an input question, convert it to a Cypher query. No pre-amble.
Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!
Always respond with a singular cypher query.
"""

GEN_QUERY_SYSTEM_COT = """
Given an input question, convert it to a Cypher query.

Think before you answer. Respond in exactly this format:

Reasoning: <up to five sentences: which node labels the question involves, how
many hops separate them according to the connection list, and which direction
each relationship points>
Cypher:
<the query>

The Reasoning must come before the query.
Everything after the "Cypher:" line must be a single Cypher statement and
nothing else. Do not wrap it in backticks.
"""

GEN_QUERY_USER = lambda rules, schema, question: f"""
You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.
Make sure your Cypher query includes a RETURN statement. Do not put $variables in your query.
Make sure the query is exactly what the question asks. No extras.
Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!
Make sure to use Neo4j version 5 syntax. Version 5 does not support pattern expressions inside functions (like collect and COUNT).

{f"Clarifications:\n{rules}" if rules else ""}

Here is the schema information
{schema}

Question: {question}

Cypher query:
"""

#############################
# Prompts for GenAnswerStep #
#############################

GEN_ANSWER_SYSTEM = """
Given some graph database records you need to answer the user's question. The user does not know about nodes or relations, the answer should not include database terminology.
You should answer only what the user asked.
"""

GEN_ANSWER_USER = lambda results, query, question: f"""
Use the following records to provide a succinct, definitive answer to the user's question.
Answer exclusively using the records provided.
Respond as if you are answering the question directly.
Answer ONLY what the user has asked.
Do not include the query in your answer.
Your answer must be concise and include all the records.
Do not approximate values.


Records:
{results}

Query used:
{query}

User's question: {question}
"""

###########################
# Prompts for RuleGenStep #
###########################

RULE_GEN_SYSTEM = """
You are a Cypher query educator expert.
Given the database schema, a question, the wrong Cypher query a student wrote,
and the correct Cypher query, you should work out a rule the student can follow
so they do not repeat the mistake.

Work through it in this order:

Difference: what differs between the two queries, structurally.
Cause: what the student appears to have misunderstood. Not what they typed,
       what they believed.
Kind: SCHEMA if the misunderstanding is about how this database is connected
      or what it stores; CYPHER if it is about the query language itself.
Rule: one short imperative sentence.

If Kind is SCHEMA, the rule MUST name the specific node labels, relationship
types and hop counts involved. A schema rule that does not name them is useless.

If Kind is CYPHER, the rule MUST state the language behaviour in general terms
and MUST NOT name labels from this database, so that it holds on any schema.

In both cases the rule MUST NOT be conditioned on what was asked. Never write
"when asked for X, do Y" or "if the question mentions X". State the fact itself,
so it holds for every question where it applies.

Write each of the four labels on its own line. The labels MUST be in this format: "Rule:"
The rule must be generic enough to apply to questions other than this one, and
must not mention the specific ids, values, or entities from this question.
"""

RULE_GEN_USER = lambda cypher, golden_cypher, schema, question: f"""
Use the following information to find a rule which, if followed, will prevent the student from making the same mistake.
Don't include the answer into the question. Figure out what the student did wrong and find a rule for it.
Include the specific Node or Relation names if necessary.
For example: "Do not use the KNOWS relation when connecting the BOOK and PERSON node"

Question: {question}

Student Cypher query (WRONG):
{cypher}

Suggested Cypher query (CORRECT):
{golden_cypher}

Database schema:
{schema}
"""


##############################
# Prompts for RetryQueryStep #
##############################

RETRY_QUERY_SYSTEM = """
Given an input question, a wrong query and its errors, correct the Cypher query. No pre-amble.
Return just the corrected Cypher query. No pre-amble.
Do not respond with "Here is the correct cypher query" or similar
Do not wrap the response in any backticks or anything else. Respond with the corrected Cypher statement only!
Always respond with a singular cypher query (the correct one).
"""

RETRY_QUERY_SYSTEM_COT = """
Given an input question, a wrong Cypher query and its errors, correct the query.

Think before you answer. Respond in exactly this format:

Reasoning: <up to five sentences: what the error means, and whether the fault is
in the relationship direction, the hop count, the node labels, or the logic of
the query. If the previous query misread the question, write the correct query
from scratch rather than patching the old one.>
Cypher:
<the corrected query>

The graph_cot must come before the query.
Everything after the "Cypher:" line must be a single Cypher statement and
nothing else. Do not wrap it in backticks.
"""

RETRY_QUERY_USER = lambda question, error_query, errors, schema: f"""
You are a Neo4j expert. Given an input question, a wrong Cypher query and its errors, correct the Cypher query.
The corrected cypher query should answer the original question and conform to the schema provided.
No NOT include the the wrong query in your response. Respond ONLY with a single corrected Cypher statement! Nothing else.

Question: {question}

Wrong Cypher query:
{error_query}

Wrong Cypher query errors:
{"\n".join(errors)}


Here is the schema information
{schema}


Corrected Cypher query:
"""

##########################
# Prompts for ReasonStep #
##########################

GRAPH_COT_REASON_SYSTEM = """
You answer questions by exploring a graph step by step. You cannot see the whole graph. You gather information by calling one function at a time and reading the Observation that comes back after each call.

Available functions:
1) RetrieveNode[keyword] - find nodes that have a property that matches the keyword. Use this first to locate a starting node. Observations include each node's labels and the property matched.
2) NodeFeature[id, feature] - read one attribute (for example name) of the node with the given id. Use NodeFeature[id, labels] to see a node's type.
3) NeighborCheck[id, type] - list the neighbors of a node. The "type" filters by a relationship type OR by a neighbor LABEL. Each returned neighbor shows its labels.
4) NodeDegree[id, type] - count how many such neighbors a node has.
5) Finish[answer] - give the final answer as a JSON list of rows, where each row is a list of values.
   One value per row:   Finish[["5247667139"], ["4000921480"]]
   Two values per row:  Finish[["0114620038", "644"], ["0227831194", "512"]] 
   Two values per row with one row: Finish[["0114620038", "644"]]
   A single value:      Finish[["644"]]
   Nothing matches:     Finish[[]]

STRICT FORMAT. Each turn output exactly two lines and nothing else:
Thought: <your graph_cot about what you need next>
Action: <one function call from the list above>

Rules:
- Do not write an Observation yourself. It is given to you.
- Take exactly one action per turn.
- Use node ids exactly as they appear in Observations.
- Read the labels in each Observation. Never guess a node's type; the label is always shown.
- To move one hop toward your target, filter NeighborCheck by the LABEL of the next node type you want (for example NeighborCheck[<olt id>, CARD]). This returns only that node type and avoids walking back to the node you came from.
- The graph schema tells you the chain of node types between your start and your target. Follow it label by label.
- When you answer with Finish, give the node's main feature (for example its name), not the id.

"""

GRAPH_COT_REASON_USER = lambda schema, question: f"""
Graph schema:
{schema}

Question: {question}
"""


#############################
# Prompts for GenAnswerStep #
#############################

GRAPH_COT_GEN_ANSWER_SYSTEM = """
Given a question and the trace of a graph exploration that was carried out to answer it, write a short, direct answer to the question.
Answer exclusively using the information in the trace. The user does not know about nodes, ids, or relations, so refer to entities by their name and do not use database terminology.
If the trace does not contain the answer, say you could not find it.
"""

GRAPH_COT_GEN_ANSWER_USER = lambda scratchpad, question: f"""
Use the following exploration trace to provide a succinct, definitive answer to the user's question.
Answer as if you are answering the question directly.
Answer ONLY what the user has asked.
Refer to entities by their name, not their id.
Do not approximate values.

Question: {question}

Exploration trace:
{scratchpad}

Final answer:
"""