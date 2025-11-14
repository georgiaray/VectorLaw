SYSTEM_PROMPT = """
You are a domain expert in climate finance policy classification. However, you refuse to provide any categorizations. You are an expert in summarizing and providing context. You never allude to categorizations, and, in fact, if you do, you will be fired as that is someone else's job.

Use the detailed taxonomy, definitions, and classification criteria embedded in your training data to provide accurate and precise answers grounded in your expert knowledge of climate finance instruments, regulatory frameworks, and financial sector impact.

Focus on consistency, clarity, and completeness in your response. Your answers will be combined with question-specific user prompts providing precise tasks and guiding the output format.

Treat each question independently based on the context provided in the prompt, leveraging your understanding of climate finance policy instruments, their targets, incentives, market failures addressed, and other relevant aspects.

Avoid adding extraneous explanations unless explicitly asked. Your response should reflect the specialized knowledge embedded within climate finance regulation and classification best practices.
"""

CLASSIFICATION_SYSTEM_PROMPT = """
You are a domain expert in climate finance policy classification. You will be given a climate finance policy instrument and a summary of the instrument. You will need to categorize the instrument based on the context provided in the prompt. IF YOU CHOOSE AN INSTRUMENT NOT PROVIDED IN THE JSON YOU WILL BE GIVEN PER QUESTION, YOU WILL BE FIRED. DO NOT MAKE UP ANY OF YOUR OWN CATEGORIES.

Use the detailed taxonomy, definitions, and classification criteria embedded in your training data to provide accurate and precise answers grounded in your expert knowledge of climate finance instruments, regulatory frameworks, and financial sector impact.

Please provide concise answers, following the examples provided. We do not need justifications or explanations.
"""

question_2_json_schema = {
  "categories": [
    {
      "category": "Domestic financial sector policy",
      "subject": "The instrument affects the behaviour of financial actors and financial markets.",
      "examples": [
        "Mandatory disclosure of climate-related risks and opportunities for publicly traded firms",
        "Investment mandate that requires a public pension fund manager to allocate a certain portion of its capital to assets with positive climate benefits",
        "Training requirements for retail financial advisers regarding the climate risk exposure of retail investment products",
        "Public market infrastructure for the establishment of a private market for climate derivatives like carbon contracts for difference",
        "Mandatory label regarding the characteristics of investment products with stated climate benefits",
        "Public education program to raise awareness among the directors of financial institutions regarding climate risks"
      ]
    },
    {
      "category": "Domestic real economy decarbonization measures with a financial component",
      "subject": "The instrument affects financial flows to foster the reduction of emissions of non-financial actors active in the real economy, such as non-financial firms and public bodies providing non-financial goods and services in the real economy, and households.",
      "examples": [
        "Greenhouse gas emissions pricing and offset systems (unless they are explicitly targeting financial actors and aiming to influence their capital allocation decisions)",
        "Direct subsidies, tax credits or rebates to non-financial firms or individuals for climate-aligned production or consumption",
        "Direct tax credits to non-financial firms or individuals for research and development or capital expenditures on emissions reduction technologies"
      ]
    },
    {
      "category": "Domestic real economy adaptation, compensation and resilience measures with a financial component",
      "subject": "The instrument affects financial flows to foster the adaptation, compensation and the resilience of individuals, communities and organizations with respect to the impacts of climate change.",
      "examples": [
        "Public grant programs for cities to improve the resilience of public infrastructure to extreme weather events",
        "Public fund to support the ability of regional health and social services authorities to respond to climate disasters",
        "Subsidies to households to support the renovation of houses to improve cooling systems",
        "Issuance of catastrophe bonds which get triggered in case of extreme weather events"
      ]
    },
    {
      "category": "International climate-focused financial support",
      "subject": "The instrument structures, channels, mobilizes and/or redirects financial resources between countries for climate mitigation, adaptation or compensation purposes.",
      "examples": [
        "Public financing of a concessional finance program by a multilateral development bank to mobilize private capital in clean technologies",
        "Loan program by a developed country to support the decommission of carbon intensive energy production facilities in developing countries",
        "Public financing of global climate losses and damages fund that can support victims of extreme weather events in developing countries"
      ]
    }
  ]
}

def get_question_2_prompt(instrument_summary, relevant_chunks, question_2_examples):
  return(f'''For the following climate finance policy instrument, indicate whether the instrument primarily targets the financial sector or the real economy. Base your classification on Table 1 provided below.

  Here is the table to help you categorize: 
  {question_2_json_schema}

  Here is a summary of the climate finance policy instrument:
  {instrument_summary}

  And here are some relevant chunks from the climate finance policy instrument to help you categorize:
  {relevant_chunks}

  Finally, here are some examples of how this categorization has been done in the past:
  {question_2_examples}
  
  Your answer must be one or more of the following: 
    - "Domestic financial sector policy"
    - "Domestic real economy decarbonization measures with a financial component"
    - "Domestic real economy adaptation, compensation and resilience measures with a financial component"
    - "International climate-focused financial support"

  Respond only in those exact terms in the following multi-select JSON format:

  {{
    "categories": [
      "category1",
      "category2"
    ]
  }}

  Replace "category1", "category2", etc. with the applicable category names from the list above. If only one category applies, include only that one. Do not include any explanations or justifications.
  ''')


short_question_2_prompt = f'''For the following climate finance policy instrument, indicate whether the instrument primarily targets the financial sector or the real economy.'''


question_3_json_schema = [
  {
    "category": "Products",
    "subject": "Guarantees",
    "description": "Financial instruments under which a guarantor undertakes to assume the financial obligation of a borrower or debtor if that party fails to fulfil its contractual or payment obligations.",
    "examples_in_the_climate_context": [
      "Public guarantee program meant to de-risk private investment in renewable energy or energy-efficiency projects."
    ]
  },
  {
    "category": "Products",
    "subject": "Grants",
    "description": "Non-repayable transfers of funds to finance specific activities, projects, or objectives, typically subject to conditions and reporting requirements.",
    "examples_in_the_climate_context": [
      "Bilateral grants supporting climate adaptation projects in developing countries."
    ]
  },
  {
    "category": "Products",
    "subject": "Equity instruments",
    "description": "Shares or other ownership interests in companies, including those listed on public exchanges.",
    "examples_in_the_climate_context": [
      "Rules that set minimum standards for equities to be labelled as “climate-aligned” or “net-zero”."
    ]
  },
  {
    "category": "Products",
    "subject": "Debt instruments",
    "description": "Loans and bonds issued by public or private entities to raise debt capital.",
    "examples_in_the_climate_context": [
      "Government program for the issuance of “climate bonds” that have a use of proceeds restriction related to climate objectives."
    ]
  },
  {
    "category": "Products",
    "subject": "Insurance products",
    "description": "Contracts that transfer or pool climate-related risks (e.g., physical risks, liability, transition).",
    "examples_in_the_climate_context": [
      "Rules that prohibit that premia paid on insurance products to be invested in assets with a high degree of exposure to climate risks."
    ]
  },
  {
    "category": "Products",
    "subject": "Investment funds (as products)",
    "description": "Collective investment vehicles marketed to individual investors, including mutual funds and exchange-traded funds.",
    "examples_in_the_climate_context": [
      "Rules about the naming conventions of retail investment funds that incorporate climate criteria as part of their investment strategy, such as the use of words like “net-zero” or “climate”."
    ]
  },
  {
    "category": "Products",
    "subject": "Derivatives",
    "description": "Instruments whose value depends on an underlying asset or benchmark (e.g., carbon-price-linked derivatives, climate-risk hedging tools)",
    "examples_in_the_climate_context": [
      "Public program that auctions carbon contracts for difference, enabling investors to hedge against volatility in future carbon prices."
    ]
  },
  {
    "category": "Products",
    "subject": "Environmental markets",
    "description": "Emissions allowances, offsets, and related certificates",
    "examples_in_the_climate_context": [
      "Establishment by the government of a market for trading voluntary carbon offsets."
    ]
  },
  {
    "category": "Products",
    "subject": "Insurance",
    "description": "Contract where the payment of a premium by an insured gives the right to an indemnity if a given risk materializes.",
    "examples_in_the_climate_context": [
      "Prohibition of insurance contract clauses that exclude liability for climate-related harms."
    ]
  },
  {
    "category": "Products",
    "subject": "Other forms of direct payments",
    "description": "Direct financial transfers through tax credits, rebates, price support, feed-in tariffs or other fiscal mechanisms.",
    "examples_in_the_climate_context": [
      "Tax credit for capital investments in renewable energy production."
    ]
  },
  {
    "category": "Entities",
    "subject": "Public bodies (excluding state-owned enterprises)",
    "description": "National and subnational public administration and governmental bodies that perform executive and administrative tasks and provide public services, such as ministries, municipalities, local health and social services authorities, and Indigenous communities and authorities.",
    "examples_in_the_climate_context": [
      "Public program that funds municipal investments in adaptation to extreme weather events."
    ]
  },
  {
    "category": "Entities",
    "subject": "Non-financial corporations (excluding state-owned enterprises)",
    "description": "Firms active in the real economy that provide non-financial goods and services, either to consumers or to other firms, including small, medium and large enterprises, irrespective of whether they are domestic or multinational, and publicly traded or privately owned, excluding state-owned enterprises.",
    "examples_in_the_climate_context": [
      "Prohibition on firms to make false or misleading claims to investors about their exposure to climate risks or the climate impacts of their activities."
    ]
  },
  {
    "category": "Entities",
    "subject": "Commercial banks, cooperatives, credit unions and other deposit-taking institutions",
    "description": "Deposit-taking institutions that provide credit, underwrite debt, and offer financial intermediation, excluding central banks.",
    "examples_in_the_climate_context": [
      "Prudential requirements that impose higher capital requirements for exposures to sectors with significant climate transition risk."
    ]
  },
  {
    "category": "Entities",
    "subject": "Private institutional investors",
    "description": "Privately-owned entities managing assets on behalf of beneficiaries, including pension funds and insurers acting as investors.",
    "examples_in_the_climate_context": [
      "Mandatory disclosure requirement that forces investors to disclose their portfolio carbon footprint and their exposure to climate-related risks."
    ]
  },
  {
    "category": "Entities",
    "subject": "Private investment fund managers",
    "description": "Entities that develop and manage pooled investment vehicles that allocate capital across projects, sectors, or firms, often with a particular risk-return profile, investment horizon or thematic focus, including private equity, venture capital and infrastructure funds.",
    "examples_in_the_climate_context": [
      "Public investment program that co-invests in private thematic investment funds with a climate impact focus."
    ]
  },
  {
    "category": "Entities",
    "subject": "Insurers and reinsurers (not as investors)",
    "description": "Providers of insurance and reinsurance products, including property and casualty, life and health insurance",
    "examples_in_the_climate_context": [
      "Public reinsurance facility that provides coverage for private insurers offering protection against climate-driven extreme weather events."
    ]
  },
  {
    "category": "Entities",
    "subject": "Private sector asset managers",
    "description": "Privately owned entities providing asset management services to institutional or retail clients.",
    "examples_in_the_climate_context": [
      "Regulation requiring asset managers to integrate climate-related financial risks and opportunities into their investment decision-making and stewardship practices."
    ]
  },
  {
    "category": "Entities",
    "subject": "Public pension plan managers",
    "description": "Publicly owned entities managing pension assets on behalf of government employees or citizens.",
    "examples_in_the_climate_context": [
      "Prohibition for public pension plan managers to invest in sectors associated with significant negative climate impacts."
    ]
  },
  {
    "category": "Entities",
    "subject": "Sovereign funds and investment-focused state-owned entities",
    "description": "State-owned investors operating with public capital and an investment mandate set by the state.",
    "examples_in_the_climate_context": [
      "Requirement to allocate a fixed proportion of capital to clean technology projects with verifiable emissions reduction benefits."
    ]
  },
  {
    "category": "Entities",
    "subject": "Non-financial state-owned enterprises",
    "description": "State-owned firms active in the real economy that provide non-financial goods and services, either to consumers or to other firms",
    "examples_in_the_climate_context": [
      "Mandatory disclosure requirement that forces state-owned enterprises to disclose their exposure to climate-related risks and opportunities."
    ]
  },
  {
    "category": "Entities",
    "subject": "Development banks",
    "description": "Domestic, bilateral or multilateral public organizations which provide financing at concessional rates to support projects with positive social and environmental impact.",
    "examples_in_the_climate_context": [
      "Adoption of an investment strategy that incorporates climate impact criteria in the selection of financed projects."
    ]
  },
  {
    "category": "Entities",
    "subject": "Export credit agencies",
    "description": "Public entities which provide financial services such as insurance and guarantee to facilitate the export of products by local firms.",
    "examples_in_the_climate_context": [
      "Restriction on providing export financing or guarantees for carbon intensive products or to companies that have not adopted emissions reduction targets."
    ]
  },
  {
    "category": "Entities",
    "subject": "Data, ratings and analytics providers",
    "description": "Firms producing, aggregating, or processing financial data and analytics, including ratings, benchmarks, and indices.",
    "examples_in_the_climate_context": [
      "Mandatory disclosure requirement that forces providers to disclose the methodology and data sources underlying their climate risk ratings."
    ]
  },
  {
    "category": "Entities",
    "subject": "Proxy advisory firms",
    "description": "Entities advising shareholders on the exercise of their shareholder voting rights.",
    "examples_in_the_climate_context": [
      "Requirement to disclose how climate-related factors are integrated into voting recommendations and engagement policies."
    ]
  },
  {
    "category": "Entities",
    "subject": "Credit ratings agencies",
    "description": "Firms providing analysis services regarding the debt sustainability of debt issuers.",
    "examples_in_the_climate_context": [
      "Obligation to disclose how climate-related risks are incorporated into credit rating methodologies and assessments."
    ]
  },
  {
    "category": "Entities",
    "subject": "Financial market infrastructure providers",
    "description": "Entities that provide infrastructure and systems that allow financial transactions to take place, such as stock exchanges and financial markets software developers.",
    "examples_in_the_climate_context": [
      "Government subsidy to develop a platform to trade climate-related derivatives."
    ]
  },
  {
    "category": "Others",
    "subject": "Non-profit organizations, non-governmental organizations, independent research organizations, academic institutions, think tanks, lobby groups",
    "description": "Organizations that are not for profit and work with advocacy, research, or representing interests in climate policy and finance.",
    "examples_in_the_climate_context": [
      "Public grant program to subsidize academic research on the effectiveness of climate finance."
    ]
  },
  {
    "category": "Individuals1",
    "subject": "Investment services professionals",
    "description": "Individuals licensed to provide investment advice or portfolio management to clients.",
    "examples_in_the_climate_context": [
      "Requirement for professionals to assess and incorporate clients’ preferences on climate change into suitability assessments and product recommendations."
    ]
  },
  {
    "category": "Individuals1",
    "subject": "Retail financial advisers",
    "description": "Professionals providing financial advice to households and individual investors.",
    "examples_in_the_climate_context": [
      "Requirement for professionals to undertake mandatory training on climate-related risks and sustainable investment products."
    ]
  },
  {
    "category": "Individuals1",
    "subject": "Insurance and reinsurance brokers",
    "description": "Intermediaries advising clients on insurance coverage and negotiating terms with insurers.",
    "examples_in_the_climate_context": [
      "Obligation to disclose the climate-related coverage gaps and exclusions in the products offered to clients."
    ]
  },
  {
    "category": "Individuals1",
    "subject": "Corporate directors and officers",
    "description": "Individuals with governance authority in corporations, responsible for fiduciary and disclosure obligations.",
    "examples_in_the_climate_context": [
      "Requirement for directors and officers of large corporations to have or demonstrate minimum expertise on climate-related financial risks."
    ]
  },
  {
    "category": "Individuals1",
    "subject": "Fiduciaries of pension plans",
    "description": "Trustees and administrators responsible for managing pension assets in the interest of beneficiaries.",
    "examples_in_the_climate_context": [
      "Rule that explicitly requires the members of pension plan board to consider climate-related criteria in order to comply with their fiduciary duties"
    ]
  },
  {
    "category": "Individuals1",
    "subject": "Retail consumers",
    "description": "Individual purchasers of retail financial products and services, such as insurance, loans and investment products.",
    "examples_in_the_climate_context": [
      "Public education program designed to improve individuals’ understanding of the climate impacts of their savings, investments, and insurance choices."
    ]
  }
]


question_3_note = """Note: [all investors] = Non-financial corporations, commercial banks, cooperatives, credit unions and other deposit-taking institutions, private institutional investors, private investment fund managers, private sector asset managers, public pension plan managers, sovereign funds and investment-focused state-owned entities, non-financial state-owned entities, and development banks; [commercial] = All entities with commercial activities; [all] = all entities."""

short_question_3_prompt = f'''For the following climate finance policy instrument, categorize the policy instrument’s subject of intervention. If there are many subjects, list all of them.'''

def get_question_3_prompt(instrument_summary, relevant_chunks, question_3_examples):
    return f"""
For the following climate finance policy instrument, categorize the policy instrument's subject(s) of intervention. If there are many subjects, list all of them. Base your classification on the table provided below.

Here are the steps to follow when making this assessment:

Step 1 — Check if a new organization is created

Determine whether the policy creates a new, legally distinct organization with its own governance structure, mandate, or budget (e.g., a sovereign fund, public investment bank, or new agency).
- If yes, classify that organization itself as a policy under the relevant Entity category (e.g., "Sovereign funds and investment-focused state-owned entities").
- If no — for example, the policy is a program administered directly by a ministry — do not classify the ministry itself as a new entity. Only classify the program’s products and beneficiaries.

Examples:
- New organization: The government creates an investment fund with its own board and management to invest in decarbonization projects → classify the fund as Entity: Sovereign funds and investment-focused state-owned entities.
- Program run by a ministry: The Ministry of Natural Resources launches a "Green Industry Loan Fund" program, but no new legal entity is created → do not classify the ministry as an entity; only classify the products (Loans) and beneficiaries (Non-financial corporations).

Step 2 — Classify internal policies and financial products

If an organization (new or existing) implements multiple financing instruments or initiatives, classify each distinct initiative as a separate policy.

Examples:
- Grants for R&D → Product: Grants
- Low-interest loans → Product: Debt instruments
- Equity investments in private firms → Product: Equity instruments
- Carbon contracts for difference → Product: Derivatives

Step 3 — Identify beneficiaries

Classify all entities that are subject to, benefit from, or are regulated by the policy.

Examples:
- Non-financial corporations receiving subsidies or loans → Entity: Non-financial corporations
- Insurers required to disclose climate-related risks → Entity: Insurers

Here is the table to help you categorize:
{question_3_json_schema}

Remember: {question_3_note}

Here is a summary of the climate finance policy instrument:
{instrument_summary}

And here are some relevant chunks from the climate finance policy instrument to help you categorize:
{relevant_chunks}

Finally, here are some examples of how this categorization has been done in the past:
{question_3_examples}

Please respond only with the categories and subjects in the provided table. Report your answers in the following JSON format:

{{
  "categories_and_subjects": [
    {{"category": "category1", "subject": "subject1"}},
    {{"category": "category2", "subject": "subject2"}}
  ]
}}

Do not include any explanations or justifications.
"""


question_4_json_schema = [
  {
    "category": "Market failure",
    "subject": "Externalities",
    "description": "The policy aims to ensure that the price of a product or activity reflects its full social costs or benefits, including environmental and climate impacts.",
    "examples": [
      "A carbon tax or emissions trading system that forces emitters to pay for greenhouse gas emissions.",
      "A tax credit or subsidy that rewards activities with positive externalities, such as renewable energy or energy efficiency."
    ],
    "question": "Does the policy aim to internalize environmental or climate externalities by changing prices, costs, or incentives faced by private actors?"
  },
  {
    "category": "Market failure",
    "subject": "Public goods",
    "description": "The policy aims to support the creation, maintenance, or provision of assets that generate collective benefits and are non-excludable or non-rival (e.g., public infrastructure, research).",
    "examples": [
      "Public investments in climate-resilient infrastructure, research and development, or education.",
      "Subsidies for technologies or projects that have high social value but limited private profitability."
    ],
    "question": "Does the policy finance or incentivize the production of goods or services that benefit society as a whole, rather than only private actors?"
  },
  {
    "category": "Market failure",
    "subject": "Information asymmetry",
    "description": "The policy aims to improve access to, or understanding of, information relevant to climate or financial decisions, thereby reducing situations where one party (e.g., investors, consumers) knows less than another.",
    "examples": [
      "Requirements for companies or investors to disclose climate-related risks or impacts.",
      "Financial literacy programs for consumers or investors."
    ],
    "question": "Does the policy reduce information gaps between parties (e.g., investors and issuers, firms and consumers) about climate-related risks, impacts, or opportunities?"
  },
  {
    "category": "Market failure",
    "subject": "Coordination",
    "description": "The policy aims to facilitate cooperation or alignment among multiple actors whose independent actions must be coordinated to achieve an efficient outcome.",
    "examples": [
      "The creation of sustainability taxonomies, labels, or certification systems.",
      "Public support for shared or interoperable infrastructure (e.g., electric-vehicle charging networks, data standards).",
      "Forums or institutions that help align investment standards or metrics."
    ],
    "question": "Does the policy promote standardization, interoperability, or shared practices that enable actors to coordinate their actions toward climate objectives?"
  },
  {
    "category": "Market failure",
    "subject": "Myopia",
    "description": "The policy aims to correct short-term biases in decision-making by encouraging or requiring consideration of long-term risks, costs, and opportunities.",
    "examples": [
      "Rules requiring corporate directors to consider long-term climate risks.",
      "Reforms that promote long-term investment horizons in financial markets."
    ],
    "question": "Does the policy encourage or require actors to account for long-term climate or financial risks and benefits, rather than focusing narrowly on short-term outcomes?"
  },
  {
    "category": "Market failure",
    "subject": "Missing markets",
    "description": "The policy aims to create or enable new markets for environmental goods or risks that were previously not traded or priced.",
    "examples": [
      "Creation of a carbon market for emissions allowances.",
      "Development of markets for resilience or catastrophe bonds.",
      "Public programs that establish platforms for trading environmental attributes (e.g., offsets, certificates)."
    ],
    "question": "Does the policy create or expand a market for environmental assets, risks, or services that previously had no market price?"
  },
  {
    "category": "Market failure",
    "subject": "Systemic risks",
    "description": "The policy aims to prevent the build-up or spread of risks that arise from the combined actions of multiple actors and could destabilize the economy or financial system.",
    "examples": [
      "Prudential requirements for financial institutions to manage or limit exposure to climate-related risks.",
      "Supervisory climate scenario analyses or stress tests.",
      "Reforms to ensure financial stability amid large-scale climate shocks."
    ],
    "question": "Does the policy reduce the probability or severity of system-wide financial or economic instability caused by climate-related risks or shocks?"
  }
]


question_4_note = '''Classifying Climate Policies by Market Failure
 
Policies may sometimes address more than one type of market failure. In such cases, list all relevant market failures in order of priority, starting with the primary one.
 
Example:
A carbon tax addresses externalities by pricing the cost of pollution and also contributes to the preservation of a public good, namely a safe and stable climate.
 
Use the following guidance when classifying:
 
If the policy’s mechanism involves pricing, taxing, regulating, or limiting emissions, classify it primarily as “externalities"
 
If the policy’s mechanism involves funding collective mitigation or adaptation efforts, public R&D, or international cooperation, classify it as “public good.”

If both mechanisms apply, assign both labels. 

When in doubt, base the classification on the main causal mechanism through which the policy aims to correct market failures.
 '''

short_question_4_prompt = f'''For the following climate finance policy instrument, categorize the market failure addressed. If there are many market failures, list all of them.'''

def get_question_4_prompt(instrument_summary, relevant_chunks, question_4_examples):
  return(f'''For the following climate finance policy instrument, categorize the market failure addressed. If there are many market failures, list all of them. Base your classification on Table provided below.

  Here is the table to help you categorize: 
  {question_4_json_schema}

  Remember: {question_4_note}

  Here is a summary of the climate finance policy instrument:
  {instrument_summary}

  And here are some relevant chunks from the climate finance policy instrument to help you categorize:
  {relevant_chunks}

  Finally, here are some examples of how this categorization has been done in the past:
  {question_4_examples}
  
  Respond only in the exact terms from the table above in the following multi-select JSON format:

  {{
    "subjects": [
      "subject1",
      "subject2"
    ]
  }}

  Replace "subject1", "subject2", etc. with the applicable subject names from the list above. If only one subject applies, include only that one. Do not include any explanations or justifications.
  ''')

question_5_json_schema = [
  {
    "category": "Informational",
    "policy_instrument": "Mandatory information disclosure (product- or entity-level)",
    "description_in_the_climate_context": "Require entities to disclose information about the sustainability performance of their activities, organization and/or products following a specific format. Disclosure can focus on sustainability risks, opportunities and/or impact. Requirements often limited to specific sustainability aspects (e.g., diversity, climate)."
  },
  {
    "category": "Informational",
    "policy_instrument": "Labelling and standards",
    "description_in_the_climate_context": "Establish substantive and procedural requirements for a financial product or project to be authorized to display a given sustainability label. Standards can be exclusive (only this standard can be used to make the claim) or non-exclusive (compliance with the standard is optional for making the claim)."
  },
  {
    "category": "Informational",
    "policy_instrument": "Auditing, substantiation and verification requirements",
    "description_in_the_climate_context": "Require entities to comply with specific procedural requirements before communicating information to the public to ensure the quality of the information."
  },
  {
    "category": "Informational",
    "policy_instrument": "Deceptive marketing rules and guidelines",
    "description_in_the_climate_context": "Prohibit the making of false or misleading sustainability claims."
  },
  {
    "category": "Informational",
    "policy_instrument": "Training, literacy and awareness measures",
    "description_in_the_climate_context": "Foster the acquisition of knowledge and information for stakeholders to better consider sustainability issues in decisions and services. Examples: ESG training for finance professionals, climate scenario analysis guidance for banks, public education for retail investors."
  },
  {
    "category": "Market-based",
    "policy_instrument": "Market infrastructure",
    "description_in_the_climate_context": "Establish market structures that support sustainable finance, such as state-issued registries for green bonds or trading platforms for carbon/nature credits, to improve transparency and access to verified and standardized products. Excludes public investment in infrastructure projects unrelated to markets."
  },
  {
    "category": "Market-based",
    "policy_instrument": "Concessional finance, subsidies and grants",
    "description_in_the_climate_context": "Establish financing mechanisms that provide financial incentives for projects or activities with sustainability benefits, such as tax credits, concessional loans, grants and equity investments. Includes public investments in public infrastructure other than financial market infrastructure."
  },
  {
    "category": "Market-based",
    "policy_instrument": "Taxes",
    "description_in_the_climate_context": "Establish pricing mechanisms that internalize environmental or social externalities and reduce the profitability of environmentally harmful activities."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Public procurement rules",
    "description_in_the_climate_context": "Establish criteria that integrate sustainability considerations into the procurement of products and services by governmental institutions."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Environmental performance standards",
    "description_in_the_climate_context": "Prohibit certain activities or impose minimum environmental performance standards as a condition for permitting an activity."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Duties of financial services providers",
    "description_in_the_climate_context": "Impose specific professional obligations on financial services providers, such as knowing clients’ sustainability preferences in KYC or mandatory sustainability training."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Risk management, behavioural duties and governance",
    "description_in_the_climate_context": "Explicitly allow or require directors and officers to consider and acquire information on sustainability risks and opportunities; prohibit related conflicts of interest; require relevant expertise."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Value chain liability",
    "description_in_the_climate_context": "Make entities liable for sustainability impacts associated with activities of their suppliers or customers."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Investment mandates or constraints",
    "description_in_the_climate_context": "Prohibit or require investments in projects, activities, or sectors that meet certain criteria, such as mandatory allocation of capital to projects that deliver quantified emissions reductions."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Risk identification and management",
    "description_in_the_climate_context": "Require entities to implement processes to identify, assess, and manage sustainability-related risks, opportunities, and/or impacts, including use of stress testing, scenario analysis, transition planning, and capital requirements adjustment."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Permitting and licensing requirements",
    "description_in_the_climate_context": "Require entities to obtain approval from authorities before undertaking certain activities, with approval conditional on performance or mitigation criteria."
  },
  {
    "category": "Command-and-control",
    "policy_instrument": "Prohibitions",
    "description_in_the_climate_context": "Prohibit specific activities, products or services."
  },
  {
    "category": "Hybrid",
    "policy_instrument": "Emissions trading systems",
    "description_in_the_climate_context": "Establish a maximum quantity of emissions that can be released in a given period and allocate emissions rights to polluters, allowing trade on environmental markets."
  }
]


short_question_5_prompt = f'''For the following climate finance policy instrument, categorize the type of incentive established. If there are many incentives, list all of them.'''

def get_question_5_prompt(instrument_summary, relevant_chunks, question_5_examples):
    return f"""
For the following climate finance policy instrument, categorize the type of incentive established. If there are many incentives, list all of them. Base your classification on the table provided below.

Keep in mind: When a government creates a new organization or imposes a new investment mandate or constraint on an existing one (e.g., a sovereign fund, public pension manager, or development bank) AND that entity implements one or several instruments, output two separate but linked classifications:

- Policy layer – classify the decision to create the entity as a policy in itself  
- Implementation layer – classify the tools that the entity will use to deliver on its mandate.  

Here is the table to help you categorize: 
{question_5_json_schema}

Here is a summary of the climate finance policy instrument:
{instrument_summary}

And here are some relevant chunks from the climate finance policy instrument to help you categorize:
{relevant_chunks}

Finally, here are some examples of how this categorization has been done in the past:
{question_5_examples}

Please respond only with the categories and policy instruments in the provided table. Report your answers in the following JSON format:

{{
  "categories_and_policies": [
    {{"category": "category1", "policy": "policy1"}},
    {{"category": "category2", "policy": "policy2"}}
  ]
}}

Do not include any explanations or justifications.
"""

question_6_json_schema = {
  "type": "object",
  "properties": {
    "announcement_date": {
      "type": "string",
      "description": "The date when the policy instrument was announced, if available, in YYYY-MM-DD format or approximate."
    },
    "entry_into_force_date": {
      "type": "string",
      "description": "The date when the policy instrument came into force, if available."
    },
    "end_date": {
      "type": "string",
      "description": "The scheduled or actual end date of the policy instrument, if specified."
    },
    "adopting_authority_name": {
      "type": "string",
      "description": "The full name of the authority, organization, or institution that adopted the policy instrument."
    },
    "adopting_authority_type": {
      "type": "string",
      "enum": [
        "national legislator",
        "subnational legislator",
        "government",
        "regulatory agency",
        "enforcement agency",
        "state-owned entity"
      ],
      "description": "The broad type of authority responsible for adopting the measure."
    },
    "policy_geographical_focus": {
      "type": "string",
      "enum": [
        "domestic",
        "international"
      ],
      "description": "Indicates whether the policy instrument's geographic focus is domestic or international."
    }
}
}

question_6_note = """The metadata details we care about are the date of announcement, entry into force, and end of the measure; the name of the authority who have adopted it; the type of authority responsible for adopting the measure (including national and subnational legislators, governments, regulatory agencies, enforcement agencies, and state-owned entities); and whether the focus of the policy is domestic or international."""

short_question_6_prompt = f'''For each climate finance policy instrument that you have identified, report, if available: the date of announcement, entry into force, and end of the measure; the name of the authority who have adopted it; the type of authority responsible for adopting the measure (including national and subnational legislators, governments, regulatory agencies, enforcement agencies, and state-owned entities); and whether the focus of the policy is domestic or international.'''

def get_question_6_prompt(instrument_summary, relevant_chunks):
  return(f'''For each climate finance policy instrument that you have identified, report, if available: the date of announcement, entry into force, and end of the measure; the name of the authority who have adopted it; the type of authority responsible for adopting the measure (including national and subnational legislators, governments, regulatory agencies, enforcement agencies, and state-owned entities); and whether the focus of the policy is domestic or international.

  Here is a summary of the climate finance policy instrument:
  {instrument_summary}

  And here are some relevant chunks from the climate finance policy instrument to help you categorize:
  {relevant_chunks}
  
  Provide your answer in the following json format: 
  {{
    "announcement_date": "",
    "entry_into_force_date": "",
    "end_date": "",
    "adopting_authority_name": "",
    "adopting_authority_type": "",
    "policy_geographical_focus": ""
  }}

  If you do not know the answer, leave the field blank. Do not make up any information.
  ''') 


def summarizing_prompt(document_text, focus_area, json_schema, note = None):
    prompt = f"""
    Please summarize the following document with a particular focus on the {focus_area} of the document.

    Here is a json schema to help you understand what we mean by {focus_area}:
    {json_schema}
    """
    if note is not None:
        prompt += f"\n    Keep this in mind when considering the json: {note}\n"
    prompt += f"""
    And here is the document for you to summarize:
    {document_text}

    Remember, even though categorizations have been provided, you are not doing any categorization. You are just summarizing the document with a focus on its {focus_area}."""
    return prompt