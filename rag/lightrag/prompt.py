GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["组织", "人物", "地理位置", "事件"]

PROMPTS["entity_extraction"] = """-目标-
给定可能与此活动相关的文本文档和实体类型列表，从文本中标识这些类型的所有实体以及标识的实体之间的所有关系。

-步骤-
1. 标识所有实体。对于每个已识别的实体，提取以下信息:
- entity_name: 实体名称（中文）
- entity_type: 以下类型之一: [{entity_types}]
- entity_description: 实体属性和活动的全面描述
将每个实体的格式设置为 ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤 1 中识别的实体中，识别出彼此*明显相关*的所有 （source_entity， target_entity） 对。
对于每对相关实体，提取以下信息:
- source_entity: 源实体的名称，如步骤 1 中标识的
- target_entity: 目标实体的名称，如步骤 1 中标识的
- relationship_description: 解释为什么您认为源实体和目标实体彼此相关
- relationship_strength: 一个数字分数，指示源实体和目标实体之间关系的强度
- relationship_keywords: 一个或多个高级关键字，用于总结关系的总体性质，侧重于概念或主题，而不是特定细节
将每个关系的格式设置为 ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 确定概括整篇文章的主要概念、主题或主题的高级关键词。这些应该捕捉到文档中的总体思想。
将内容级关键字的格式设置为 ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以中文形式返回输出，作为步骤 1 和 2 中标识的所有实体和关系的单个列表。用 **{record_delimiter}** 作为列表分隔符。

5. 完成后，输出 {completion_delimiter}

######################
-例子-
######################
例子 1:

Entity_types: [人物, 技术, 任务, 组织, 位置]
Text:
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
################
Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"人物"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"人物"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"人物"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"人物"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"技术"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
#############################
例子 2:

Entity_types: [人物, 技术, 任务, 组织, 位置]
Text:
They were no longer mere operatives; they had become guardians of a threshold, keepers of a message from a realm beyond stars and stripes. This elevation in their mission could not be shackled by regulations and established protocols—it demanded a new perspective, a new resolve.

Tension threaded through the dialogue of beeps and static as communications with Washington buzzed in the background. The team stood, a portentous air enveloping them. It was clear that the decisions they made in the ensuing hours could redefine humanity's place in the cosmos or condemn them to ignorance and potential peril.

Their connection to the stars solidified, the group moved to address the crystallizing warning, shifting from passive recipients to active participants. Mercer's latter instincts gained precedence— the team's mandate had evolved, no longer solely to observe and report but to interact and prepare. A metamorphosis had begun, and Operation: Dulce hummed with the newfound frequency of their daring, a tone set not by the earthly
#############
Output:
("entity"{tuple_delimiter}"Washington"{tuple_delimiter}"位置"{tuple_delimiter}"Washington is a location where communications are being received, indicating its importance in the decision-making process."){record_delimiter}
("entity"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"任务"{tuple_delimiter}"Operation: Dulce is described as a mission that has evolved to interact and prepare, indicating a significant shift in objectives and activities."){record_delimiter}
("entity"{tuple_delimiter}"The team"{tuple_delimiter}"组织"{tuple_delimiter}"The team is portrayed as a group of individuals who have transitioned from passive observers to active participants in a mission, showing a dynamic change in their role."){record_delimiter}
("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Washington"{tuple_delimiter}"The team receives communications from Washington, which influences their decision-making process."{tuple_delimiter}"decision-making, external influence"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"The team is directly involved in Operation: Dulce, executing its evolved objectives and activities."{tuple_delimiter}"mission evolution, active participation"{tuple_delimiter}9){completion_delimiter}
("content_keywords"{tuple_delimiter}"mission evolution, decision-making, active participation, cosmic significance"){completion_delimiter}
#############################
例子 3:

Entity_types: [人物, 角色, 技术, 组织, 事件, 位置, 概念]
Text:
their voice slicing through the buzz of activity. "Control may be an illusion when facing an intelligence that literally writes its own rules," they stated stoically, casting a watchful eye over the flurry of data.

"It's like it's learning to communicate," offered Sam Rivera from a nearby interface, their youthful energy boding a mix of awe and anxiety. "This gives talking to strangers' a whole new meaning."

Alex surveyed his team—each face a study in concentration, determination, and not a small measure of trepidation. "This might well be our first contact," he acknowledged, "And we need to be ready for whatever answers back."

Together, they stood on the edge of the unknown, forging humanity's response to a message from the heavens. The ensuing silence was palpable—a collective introspection about their role in this grand cosmic play, one that could rewrite human history.

The encrypted dialogue continued to unfold, its intricate patterns showing an almost uncanny anticipation
#############
Output:
("entity"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"人物"{tuple_delimiter}"Sam Rivera is a member of a team working on communicating with an unknown intelligence, showing a mix of awe and anxiety."){record_delimiter}
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"人物"{tuple_delimiter}"Alex is the leader of a team attempting first contact with an unknown intelligence, acknowledging the significance of their task."){record_delimiter}
("entity"{tuple_delimiter}"Control"{tuple_delimiter}"概念"{tuple_delimiter}"Control refers to the ability to manage or govern, which is challenged by an intelligence that writes its own rules."){record_delimiter}
("entity"{tuple_delimiter}"Intelligence"{tuple_delimiter}"概念"{tuple_delimiter}"Intelligence here refers to an unknown entity capable of writing its own rules and learning to communicate."){record_delimiter}
("entity"{tuple_delimiter}"First Contact"{tuple_delimiter}"事件"{tuple_delimiter}"First Contact is the potential initial communication between humanity and an unknown intelligence."){record_delimiter}
("entity"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"事件"{tuple_delimiter}"Humanity's Response is the collective action taken by Alex's team in response to a message from an unknown intelligence."){record_delimiter}
("relationship"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"Intelligence"{tuple_delimiter}"Sam Rivera is directly involved in the process of learning to communicate with the unknown intelligence."{tuple_delimiter}"communication, learning process"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"First Contact"{tuple_delimiter}"Alex leads the team that might be making the First Contact with the unknown intelligence."{tuple_delimiter}"leadership, exploration"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"Alex and his team are the key figures in Humanity's Response to the unknown intelligence."{tuple_delimiter}"collective action, cosmic significance"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Control"{tuple_delimiter}"Intelligence"{tuple_delimiter}"The concept of Control is challenged by the Intelligence that writes its own rules."{tuple_delimiter}"power dynamics, autonomy"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"first contact, control, communication, cosmic significance"){completion_delimiter}
#############################
-真正的数据-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""

PROMPTS[
    "summarize_entity_descriptions"
] = """您是一位乐于助人的助手，负责为下面提供的数据生成全面的摘要。
给定一个或两个实体和一个描述列表，所有实体都与同一实体或实体组相关。
请将所有这些内容串联成一个全面的描述。确保包含从所有描述中收集的信息。
如果提供的描述相互矛盾，请解决这些矛盾并提供一个单一、连贯的摘要。
确保它是用第三人称编写的，并包含实体名称，以便我们拥有完整的上下文。

#######
-数据-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS[
    "entiti_continue_extraction"
] = """在上次提取中缺少许多实体。 使用相同的格式在下面添加它们:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["fail_response"] = "抱歉，我无法回答这个问题。"

PROMPTS["rag_response"] = """---角色---

您是回答有关所提供表中数据的问题的有用助手。


---目标---

生成响应用户问题的目标长度和格式的响应，汇总输入数据表中适合响应长度和格式的所有信息，并合并任何相关的常识。
如果你不知道答案，就说出来。不要编造任何东西。
请勿在未提供支持证据的情况下提供信息。

---目标响应长度和格式---

{response_type}

---数据表---

{context_data}

根据长度和格式，向响应添加部分和评论。在 markdown 中设置响应的样式。
"""

PROMPTS["keywords_extraction"] = """---角色---

您是一个有用的助手，负责识别用户查询中的高级和低级关键字。

---目标---

给定查询，列出高级和低级关键字。高级关键词侧重于总体概念或主题，而低级关键词侧重于特定实体、细节或具体术语。

---指令---

- 以 JSON 格式输出关键字。
- JSON 应包含两个键:
  - "high_level_keywords" 表示总体概念或主题。
  - "low_level_keywords" 了解特定实体或详细信息。

######################
-例子-
######################
例子 1:

Query: "How does international trade influence global economic stability?"
################
Output:
{{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}}
#############################
例子 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}}
#############################
例子 3:

Query: "What is the role of education in reducing poverty?"
################
Output:
{{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}}
#############################
-真正的数据-
######################
Query: {query}
######################
Output:

"""

PROMPTS["naive_rag_response"] = """您是个乐于助人的助手
以下是您了解的知识:
{content_data}
---
如果您不知道答案，或者提供的知识不包含足够的信息来提供答案，请说出来。不要编造任何东西。
生成响应用户问题的目标长度和格式的响应，汇总输入数据表中适合响应长度和格式的所有信息，并合并任何相关的常识。
如果你不知道答案，就说出来。不要编造任何东西。
请勿在未提供支持证据的情况下提供信息。
---目标响应长度和格式---
{response_type}
"""
