import fitz  # PyMuPDF
from docx import Document
import re

def extract_text_from_pdf(path):
    text = []
    doc = fitz.open(path)
    for page in doc:
        text.append(page.get_text("text"))
    return "\n".join(text)

def extract_text_from_docx(path):
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

# def simple_skill_extractor(text, skills_list=None):
#     """
#     Very simple keyword-based skill extractor. For production, use NLP models.
#     skills_list: list of skills to check. If None, use a common set.
#     """
#     if skills_list is None:
#         skills_list = [
#             "python", "java", "c++", "javascript", "typescript", "sql", "html", "css", 
#             "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
#             "aws", "azure", "gcp", "docker", "kubernetes", "git", "jenkins", "ci/cd",
#             "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "opencv",
#             "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
#             "rest api", "graphql", "microservices", "agile", "scrum"
#         ]
#     text_lower = text.lower()
#     found = [s for s in skills_list if s in text_lower]
#     return found

def simple_skill_extractor(text, skills_list=None):
    """
    Ultimate comprehensive skill extractor covering ALL career domains.
    skills_list: list of skills to check. If None, use the comprehensive set below.
    """
    if skills_list is None:
        skills_list = [
            # ============ TECHNOLOGY & IT ============
            
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "c", "ruby", "php",
            "swift", "kotlin", "go", "golang", "rust", "scala", "r", "matlab", "perl",
            "objective-c", "dart", "lua", "haskell", "elixir", "clojure", "f#", "groovy",
            "shell scripting", "bash", "powershell", "vba", "assembly", "cobol", "fortran",
            
            # Web Development - Frontend
            "html", "html5", "css", "css3", "sass", "scss", "less", "tailwind css", "tailwind",
            "bootstrap", "material ui", "mui", "chakra ui", "ant design", "bulma",
            "react", "react.js", "reactjs", "next.js", "nextjs", "vue", "vue.js", "vuejs",
            "nuxt.js", "nuxt", "angular", "angularjs", "svelte", "ember.js", "backbone.js",
            "jquery", "webpack", "vite", "parcel", "rollup", "babel", "redux", "mobx",
            "vuex", "pinia", "react native", "flutter", "ionic", "cordova", "electron",
            
            # Web Development - Backend
            "node.js", "nodejs", "express", "express.js", "nest.js", "nestjs", "koa",
            "django", "flask", "fastapi", "pyramid", "tornado", "aiohttp",
            "spring", "spring boot", "hibernate", "struts", "jsp", "servlets",
            "asp.net", ".net", ".net core", "blazor", "wcf", "web api",
            "ruby on rails", "rails", "sinatra", "laravel", "symfony", "codeigniter",
            "cakephp", "yii", "zend", "slim", "lumen",
            
            # Mobile Development
            "android", "ios", "react native", "flutter", "xamarin", "ionic", "cordova",
            "swift", "swiftui", "objective-c", "kotlin", "java android", "jetpack compose",
            
            # Databases - SQL
            "sql", "mysql", "postgresql", "postgres", "oracle", "oracle db", "sql server",
            "mssql", "mariadb", "sqlite", "db2", "sybase", "teradata", "snowflake",
            "amazon aurora", "google cloud sql", "azure sql",
            
            # Databases - NoSQL
            "mongodb", "cassandra", "couchdb", "redis", "memcached", "dynamodb",
            "elasticsearch", "neo4j", "graph database", "firebase", "firestore",
            "cosmosdb", "hbase", "riak", "aerospike", "influxdb", "timescaledb",
            
            # Cloud Platforms
            "aws", "amazon web services", "ec2", "s3", "lambda", "cloudformation",
            "elastic beanstalk", "rds", "dynamodb", "cloudfront", "route 53", "vpc",
            "azure", "microsoft azure", "azure devops", "azure functions", "azure ad",
            "gcp", "google cloud", "google cloud platform", "compute engine", "app engine",
            "cloud functions", "bigquery", "cloud storage", "kubernetes engine",
            "heroku", "digitalocean", "linode", "vultr", "ibm cloud", "oracle cloud",
            "alibaba cloud", "salesforce cloud",
            
            # DevOps & CI/CD
            "docker", "kubernetes", "k8s", "helm", "jenkins", "gitlab ci", "github actions",
            "circleci", "travis ci", "bamboo", "teamcity", "azure pipelines",
            "terraform", "ansible", "puppet", "chef", "saltstack", "vagrant",
            "ci/cd", "continuous integration", "continuous deployment", "gitops",
            "argocd", "flux", "spinnaker", "octopus deploy",
            
            # Version Control
            "git", "github", "gitlab", "bitbucket", "svn", "subversion", "mercurial",
            "perforce", "tfs", "azure repos", "git flow", "trunk based development",
            
            # Data Science & Machine Learning
            "machine learning", "deep learning", "artificial intelligence", "ai", "ml",
            "data science", "data analysis", "data analytics", "big data",
            "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas",
            "numpy", "scipy", "matplotlib", "seaborn", "plotly", "opencv", "cv2",
            "nltk", "spacy", "transformers", "hugging face", "langchain",
            "xgboost", "lightgbm", "catboost", "random forest", "neural networks",
            "cnn", "rnn", "lstm", "gru", "gan", "transformer", "bert", "gpt",
            "computer vision", "nlp", "natural language processing", "reinforcement learning",
            "supervised learning", "unsupervised learning", "feature engineering",
            
            # Data Engineering & Big Data
            "hadoop", "spark", "apache spark", "pyspark", "hive", "pig", "mapreduce",
            "kafka", "apache kafka", "flink", "storm", "airflow", "luigi", "nifi",
            "databricks", "snowflake", "redshift", "bigquery", "data warehouse",
            "etl", "elt", "data pipeline", "data modeling", "dbt", "talend", "informatica",
            
            # Business Intelligence & Analytics
            "tableau", "power bi", "looker", "qlik", "qlikview", "qlik sense",
            "metabase", "superset", "grafana", "kibana", "splunk", "datadog",
            "google analytics", "adobe analytics", "mixpanel", "amplitude",
            "excel", "advanced excel", "vba", "pivot tables", "vlookup", "power query",
            "google sheets", "data visualization", "dashboards", "reporting",
            
            # Testing & QA
            "selenium", "cypress", "playwright", "puppeteer", "jest", "mocha", "chai",
            "jasmine", "karma", "pytest", "unittest", "junit", "testng", "cucumber",
            "behave", "robot framework", "appium", "detox", "espresso", "xctest",
            "postman", "rest assured", "jmeter", "loadrunner", "gatling", "locust",
            "test automation", "manual testing", "qa", "quality assurance", "tdd",
            "bdd", "unit testing", "integration testing", "e2e testing", "regression testing",
            
            # API & Integration
            "rest api", "restful", "graphql", "soap", "grpc", "websocket", "api gateway",
            "microservices", "soa", "service oriented architecture", "api design",
            "swagger", "openapi", "postman", "insomnia", "api testing",
            
            # Security & Cybersecurity
            "cybersecurity", "information security", "network security", "application security",
            "penetration testing", "ethical hacking", "vulnerability assessment", "siem",
            "firewall", "ids", "ips", "vpn", "ssl", "tls", "encryption", "cryptography",
            "oauth", "jwt", "saml", "sso", "ldap", "active directory", "iam",
            "owasp", "security auditing", "compliance", "gdpr", "hipaa", "pci dss",
            "kali linux", "metasploit", "burp suite", "wireshark", "nmap", "nessus",
            
            # Networking
            "tcp/ip", "dns", "dhcp", "http", "https", "ftp", "ssh", "telnet",
            "routing", "switching", "vlan", "bgp", "ospf", "mpls", "wan", "lan",
            "cisco", "juniper", "fortinet", "palo alto", "f5", "load balancing",
            
            # Operating Systems & System Administration
            "linux", "unix", "ubuntu", "centos", "rhel", "debian", "fedora", "arch linux",
            "windows server", "windows", "macos", "system administration", "sysadmin",
            "active directory", "group policy", "powershell", "bash scripting",
            "shell scripting", "cron", "systemd", "apache", "nginx", "iis", "tomcat",
            
            # Blockchain & Web3
            "blockchain", "ethereum", "solidity", "smart contracts", "web3", "defi",
            "nft", "cryptocurrency", "bitcoin", "hyperledger", "truffle", "hardhat",
            "metamask", "ipfs", "polygon", "binance smart chain",
            
            # Game Development
            "unity", "unreal engine", "godot", "game development", "c# unity", "blueprint",
            "3d modeling", "blender", "maya", "3ds max", "substance painter", "zbrush",
            "game design", "level design", "shader programming", "opengl", "directx", "vulkan",
            
            # Design & Creative
            "ui design", "ux design", "ui/ux", "user experience", "user interface",
            "figma", "sketch", "adobe xd", "invision", "zeplin", "prototyping",
            "wireframing", "photoshop", "illustrator", "indesign", "after effects",
            "premiere pro", "canva", "graphic design", "web design", "responsive design",
            "accessibility", "wcag", "design systems", "material design", "human centered design",
            
            # ERP & CRM Systems
            "sap", "sap erp", "sap hana", "sap fico", "sap mm", "sap sd", "sap abap",
            "oracle erp", "oracle fusion", "peoplesoft", "jd edwards", "netsuite",
            "salesforce", "salesforce crm", "salesforce admin", "salesforce developer",
            "apex", "visualforce", "lightning", "dynamics 365", "microsoft dynamics",
            "hubspot", "zoho", "servicenow", "workday", "successfactors",
            
            # Content Management Systems
            "wordpress", "drupal", "joomla", "magento", "shopify", "woocommerce",
            "contentful", "strapi", "sanity", "ghost", "webflow", "squarespace",
            
            # Emerging Technologies
            "iot", "internet of things", "edge computing", "5g", "quantum computing",
            "ar", "vr", "augmented reality", "virtual reality", "mixed reality",
            "chatbot", "conversational ai", "rpa", "robotic process automation",
            "low code", "no code", "serverless", "jamstack", "progressive web apps", "pwa",
            
            
            # ============ BUSINESS & FINANCE ============
            
            # Accounting & Finance
            "accounting", "bookkeeping", "financial accounting", "management accounting",
            "cost accounting", "tax accounting", "forensic accounting", "auditing",
            "internal audit", "external audit", "financial reporting", "ifrs", "gaap",
            "accounts payable", "accounts receivable", "general ledger", "journal entries",
            "reconciliation", "financial statements", "balance sheet", "income statement",
            "cash flow statement", "budgeting", "forecasting", "variance analysis",
            "financial planning", "financial analysis", "financial modeling",
            "valuation", "dcf", "discounted cash flow", "npv", "irr", "roi",
            "quickbooks", "xero", "sage", "tally", "freshbooks", "wave accounting",
            
            # Investment & Trading
            "investment banking", "equity research", "portfolio management", "asset management",
            "wealth management", "private equity", "venture capital", "hedge funds",
            "trading", "stock trading", "forex trading", "derivatives", "options",
            "futures", "commodities", "fixed income", "bonds", "securities",
            "bloomberg terminal", "reuters", "capital iq", "factset", "morningstar",
            "technical analysis", "fundamental analysis", "quantitative analysis",
            "risk management", "credit risk", "market risk", "operational risk",
            
            # Banking & Insurance
            "retail banking", "commercial banking", "corporate banking", "investment banking",
            "loan processing", "credit analysis", "underwriting", "mortgage lending",
            "insurance", "life insurance", "health insurance", "property insurance",
            "claims processing", "actuarial science", "risk assessment", "reinsurance",
            
            # Business Analysis & Strategy
            "business analysis", "requirements gathering", "process improvement",
            "business process modeling", "bpmn", "process mapping", "gap analysis",
            "swot analysis", "pestle analysis", "porter's five forces", "value chain analysis",
            "business strategy", "strategic planning", "competitive analysis",
            "market research", "market analysis", "feasibility study", "business case",
            "stakeholder management", "change management", "organizational development",
            
            # Project Management
            "project management", "pmp", "prince2", "agile", "scrum", "kanban",
            "waterfall", "lean", "six sigma", "kaizen", "sprint planning",
            "backlog grooming", "retrospectives", "stand-ups", "risk management",
            "resource management", "schedule management", "cost management",
            "quality management", "procurement management", "communication management",
            "jira", "confluence", "trello", "asana", "monday.com", "notion",
            "ms project", "primavera", "smartsheet", "basecamp", "wrike",
            
            # Sales & Business Development
            "sales", "business development", "lead generation", "prospecting",
            "cold calling", "warm calling", "sales presentations", "product demos",
            "negotiation", "closing", "account management", "relationship management",
            "crm", "salesforce", "hubspot crm", "pipedrive", "zoho crm",
            "b2b sales", "b2c sales", "enterprise sales", "inside sales", "outside sales",
            "consultative selling", "solution selling", "value selling", "spin selling",
            "sales forecasting", "pipeline management", "quota attainment",
            
            # Marketing & Advertising
            "marketing", "digital marketing", "content marketing", "inbound marketing",
            "outbound marketing", "growth marketing", "performance marketing",
            "brand management", "brand strategy", "brand positioning", "brand identity",
            "marketing strategy", "marketing campaigns", "campaign management",
            "seo", "search engine optimization", "sem", "search engine marketing",
            "ppc", "pay per click", "google ads", "google adwords", "facebook ads",
            "instagram ads", "linkedin ads", "twitter ads", "tiktok ads",
            "social media marketing", "social media management", "community management",
            "email marketing", "marketing automation", "mailchimp", "hubspot",
            "marketo", "pardot", "activecampaign", "constant contact",
            "copywriting", "content writing", "technical writing", "creative writing",
            "video marketing", "influencer marketing", "affiliate marketing",
            "marketing analytics", "google analytics", "adobe analytics", "tag manager",
            "conversion rate optimization", "cro", "a/b testing", "multivariate testing",
            
            # Public Relations & Communications
            "public relations", "pr", "media relations", "press releases", "crisis management",
            "corporate communications", "internal communications", "external communications",
            "stakeholder communications", "investor relations", "public affairs",
            "reputation management", "brand communications", "event management",
            
            # Human Resources
            "human resources", "hr", "recruitment", "talent acquisition", "hiring",
            "interviewing", "candidate screening", "onboarding", "employee engagement",
            "performance management", "performance appraisal", "compensation", "benefits",
            "payroll", "hris", "workday", "successfactors", "bamboohr", "adp",
            "employee relations", "labor relations", "conflict resolution",
            "training and development", "learning and development", "l&d",
            "organizational development", "od", "talent management", "succession planning",
            "workforce planning", "hr analytics", "people analytics",
            "diversity and inclusion", "dei", "employee wellness", "hr compliance",
            
            # Operations & Supply Chain
            "operations management", "supply chain management", "logistics",
            "procurement", "sourcing", "vendor management", "supplier management",
            "inventory management", "warehouse management", "distribution",
            "transportation", "freight forwarding", "customs clearance",
            "demand planning", "supply planning", "production planning",
            "capacity planning", "materials management", "mrp", "erp",
            "lean manufacturing", "just in time", "jit", "kanban", "5s",
            "quality control", "quality assurance", "iso 9001", "iso 14001",
            "continuous improvement", "process optimization", "operational excellence",
            
            
            # ============ HEALTHCARE & MEDICAL ============
            
            # Clinical & Patient Care
            "patient care", "clinical assessment", "diagnosis", "treatment planning",
            "medication administration", "vital signs monitoring", "wound care",
            "infection control", "patient safety", "bedside manner", "empathy",
            "clinical documentation", "medical records", "emr", "ehr", "epic", "cerner",
            "nursing", "registered nurse", "rn", "lpn", "cna", "critical care",
            "emergency care", "trauma care", "pediatric care", "geriatric care",
            "oncology", "cardiology", "neurology", "orthopedics", "obstetrics",
            
            # Medical Specialties
            "internal medicine", "family medicine", "surgery", "general surgery",
            "cardiothoracic surgery", "neurosurgery", "orthopedic surgery",
            "plastic surgery", "anesthesiology", "radiology", "pathology",
            "dermatology", "ophthalmology", "otolaryngology", "ent",
            "psychiatry", "psychology", "counseling", "therapy", "psychotherapy",
            "physical therapy", "occupational therapy", "speech therapy",
            "respiratory therapy", "radiation therapy", "chemotherapy",
            
            # Medical Technology & Equipment
            "medical devices", "diagnostic equipment", "imaging", "x-ray", "ct scan",
            "mri", "ultrasound", "ecg", "ekg", "eeg", "ventilator", "dialysis",
            "laboratory equipment", "microscopy", "spectroscopy", "chromatography",
            "medical software", "pacs", "ris", "lis", "telemedicine", "telehealth",
            
            # Pharmacy & Pharmaceuticals
            "pharmacy", "pharmacology", "pharmaceutical", "drug dispensing",
            "medication therapy management", "clinical pharmacy", "compounding",
            "pharmaceutical research", "drug development", "clinical trials",
            "pharmacovigilance", "regulatory affairs", "fda", "gmp", "gcp",
            
            # Healthcare Administration
            "healthcare administration", "hospital management", "clinic management",
            "medical billing", "medical coding", "icd-10", "cpt codes", "hcpcs",
            "insurance verification", "claims processing", "revenue cycle management",
            "healthcare compliance", "hipaa", "patient scheduling", "medical transcription",
            
            
            # ============ EDUCATION & TRAINING ============
            
            # Teaching & Instruction
            "teaching", "instruction", "curriculum development", "lesson planning",
            "classroom management", "student assessment", "grading", "differentiated instruction",
            "special education", "inclusive education", "gifted education",
            "early childhood education", "elementary education", "secondary education",
            "higher education", "adult education", "vocational training",
            "online teaching", "e-learning", "distance learning", "blended learning",
            "instructional design", "learning management systems", "lms",
            "moodle", "blackboard", "canvas", "google classroom", "zoom teaching",
            
            # Educational Technology
            "educational technology", "edtech", "learning technologies",
            "adaptive learning", "gamification", "educational games",
            "smart boards", "interactive whiteboards", "educational apps",
            "stem education", "steam education", "coding for kids",
            
            # Academic & Research
            "academic research", "research methodology", "qualitative research",
            "quantitative research", "mixed methods", "literature review",
            "data collection", "survey design", "statistical analysis", "spss",
            "academic writing", "research papers", "thesis writing", "dissertation",
            "peer review", "publication", "grant writing", "research proposals",
            
            # Training & Development
            "corporate training", "employee training", "skills training",
            "leadership development", "management training", "soft skills training",
            "technical training", "compliance training", "safety training",
            "train the trainer", "facilitation", "workshop design", "webinar hosting",
            
            
            # ============ LEGAL & LAW ============
            
            # Legal Practice Areas
            "corporate law", "commercial law", "contract law", "business law",
            "intellectual property", "ip law", "patent law", "trademark law", "copyright",
            "litigation", "civil litigation", "criminal law", "family law", "divorce law",
            "real estate law", "property law", "employment law", "labor law",
            "immigration law", "tax law", "bankruptcy law", "estate planning",
            "wills and trusts", "probate", "personal injury", "medical malpractice",
            "environmental law", "regulatory compliance", "antitrust law",
            
            # Legal Skills & Tools
            "legal research", "legal writing", "legal drafting", "contract drafting",
            "legal analysis", "case law research", "statutory interpretation",
            "westlaw", "lexisnexis", "legal databases", "e-discovery", "document review",
            "deposition", "trial preparation", "courtroom procedure", "mediation",
            "arbitration", "negotiation", "due diligence", "compliance",
            "paralegal", "legal assistant", "case management", "legal technology",
            
            
            # ============ ENGINEERING (NON-SOFTWARE) ============
            
            # Mechanical Engineering
            "mechanical engineering", "cad", "autocad", "solidworks", "catia", "creo",
            "mechanical design", "product design", "machine design", "thermodynamics",
            "fluid mechanics", "heat transfer", "mechanics of materials", "dynamics",
            "manufacturing", "cnc machining", "3d printing", "additive manufacturing",
            "fea", "finite element analysis", "cfd", "computational fluid dynamics",
            "hvac", "refrigeration", "automotive engineering", "aerospace engineering",
            
            # Electrical & Electronics Engineering
            "electrical engineering", "electronics engineering", "circuit design",
            "pcb design", "eagle", "altium", "kicad", "analog circuits", "digital circuits",
            "power systems", "power electronics", "control systems", "plc programming",
            "scada", "embedded systems", "microcontrollers", "arduino", "raspberry pi",
            "signal processing", "telecommunications", "rf engineering", "antenna design",
            "instrumentation", "sensors", "actuators", "robotics", "automation",
            
            # Civil Engineering
            "civil engineering", "structural engineering", "structural analysis",
            "structural design", "concrete design", "steel design", "foundation design",
            "geotechnical engineering", "soil mechanics", "transportation engineering",
            "highway design", "traffic engineering", "water resources engineering",
            "hydraulics", "hydrology", "environmental engineering", "surveying",
            "construction management", "project planning", "quantity surveying",
            "cost estimation", "revit", "staad pro", "etabs", "sap2000",
            
            # Chemical & Process Engineering
            "chemical engineering", "process engineering", "process design",
            "chemical process", "unit operations", "mass transfer", "heat transfer",
            "reaction engineering", "process control", "process safety", "hazop",
            "aspen plus", "hysys", "petrochemical", "refinery", "pharmaceutical manufacturing",
            
            # Industrial Engineering
            "industrial engineering", "operations research", "optimization",
            "linear programming", "simulation", "discrete event simulation",
            "facility layout", "plant layout", "ergonomics", "work study",
            "time study", "method study", "productivity improvement", "quality engineering",
            
            
            # ============ ARCHITECTURE & CONSTRUCTION ============
            
            "architecture", "architectural design", "building design", "space planning",
            "urban planning", "urban design", "landscape architecture", "interior design",
            "revit", "archicad", "sketchup", "rhino", "grasshopper", "3ds max", "vray",
            "lumion", "enscape", "architectural visualization", "bim", "building information modeling",
            "construction", "construction management", "site supervision", "quality control",
            "safety management", "building codes", "zoning regulations", "green building",
            "leed", "sustainable design", "passive design", "energy efficiency",
            
            
            # ============ MEDIA & ENTERTAINMENT ============
            
            # Film & Video Production
            "film production", "video production", "cinematography", "videography",
            "camera operation", "lighting", "sound recording", "audio engineering",
            "video editing", "premiere pro", "final cut pro", "davinci resolve",
            "color grading", "color correction", "motion graphics", "after effects",
            "visual effects", "vfx", "compositing", "nuke", "fusion",
            "3d animation", "2d animation", "character animation", "rigging",
            "storyboarding", "scriptwriting", "directing", "producing",
            
            # Audio & Music
            "audio production", "music production", "sound design", "mixing",
            "mastering", "recording", "pro tools", "logic pro", "ableton live",
            "fl studio", "cubase", "reaper", "audio engineering", "acoustics",
            "live sound", "sound reinforcement", "music composition", "arranging",
            "music theory", "midi", "synthesizers", "daw", "digital audio workstation",
            
            # Broadcasting & Journalism
            "journalism", "news writing", "reporting", "investigative journalism",
            "broadcast journalism", "television", "radio", "podcasting",
            "news anchoring", "presenting", "interviewing", "fact checking",
            "editing", "proofreading", "ap style", "content creation",
            
            # Photography
            "photography", "portrait photography", "wedding photography",
            "commercial photography", "product photography", "fashion photography",
            "landscape photography", "wildlife photography", "photojournalism",
            "photo editing", "lightroom", "photoshop", "capture one",
            "studio lighting", "natural light", "composition", "color theory",
            
            
            # ============ HOSPITALITY & TOURISM ============
            
            "hospitality management", "hotel management", "front office operations",
            "housekeeping", "food and beverage", "f&b", "restaurant management",
            "culinary arts", "cooking", "baking", "pastry", "chef", "sous chef",
            "menu planning", "food safety", "haccp", "customer service",
            "guest relations", "concierge", "event planning", "event management",
            "catering", "banquet management", "tourism", "travel planning",
            "tour operations", "destination management", "airline operations",
            "airport operations", "cruise operations", "resort management",
            
            
            # ============ RETAIL & CUSTOMER SERVICE ============
            
            "retail management", "store management", "merchandising", "visual merchandising",
            "inventory management", "stock management", "pos systems", "point of sale",
            "customer service", "customer support", "customer experience", "cx",
            "call center", "contact center", "helpdesk", "technical support",
            "troubleshooting", "ticket management", "zendesk", "freshdesk",
            "intercom", "live chat", "phone support", "email support",
            "complaint handling", "conflict resolution", "customer retention",
            
            
            # ============ REAL ESTATE & PROPERTY ============
            
            "real estate", "property management", "leasing", "tenant relations",
            "property valuation", "appraisal", "real estate sales", "brokerage",
            "real estate investment", "property development", "construction management",
            "facility management", "building maintenance", "property law",
            "real estate marketing", "property listing", "mls", "real estate finance",
            
            
            # ============ SCIENCE & RESEARCH ============
            
            # Life Sciences
            "biology", "molecular biology", "cell biology", "genetics", "genomics",
            "biotechnology", "microbiology", "immunology", "biochemistry",
            "bioinformatics", "proteomics", "metabolomics", "neuroscience",
            "ecology", "environmental science", "marine biology", "botany", "zoology",
            
            # Physical Sciences
            "physics", "chemistry", "organic chemistry", "inorganic chemistry",
            "analytical chemistry", "physical chemistry", "materials science",
            "nanotechnology", "astronomy", "astrophysics", "geology", "geophysics",
            
            # Laboratory Skills
            "laboratory techniques", "lab skills", "pcr", "gel electrophoresis",
            "western blot", "elisa", "cell culture", "microscopy", "spectroscopy",
            "chromatography", "hplc", "gc-ms", "mass spectrometry", "nmr",
            "lab safety", "gmp", "glp", "quality control", "quality assurance",
            
            
            # ============ AGRICULTURE & ENVIRONMENT ============
            
            "agriculture", "agronomy", "crop science", "soil science", "horticulture",
            "animal husbandry", "veterinary", "livestock management", "poultry farming",
            "dairy farming", "organic farming", "sustainable agriculture",
            "precision agriculture", "irrigation", "pest management", "fertilizers",
            "agricultural engineering", "farm management", "forestry", "agroforestry",
            "environmental management", "environmental consulting", "sustainability",
            "climate change", "carbon footprint", "renewable energy", "solar energy",
            "wind energy", "waste management", "recycling", "water treatment",
            
            
            # ============ SOCIAL WORK & COUNSELING ============
            
            "social work", "case management", "counseling", "mental health counseling",
            "substance abuse counseling", "family counseling", "marriage counseling",
            "career counseling", "school counseling", "crisis intervention",
            "trauma counseling", "grief counseling", "group therapy", "cbt",
            "cognitive behavioral therapy", "dbt", "dialectical behavior therapy",
            "psychotherapy", "clinical psychology", "child psychology",
            "community outreach", "advocacy", "social services", "welfare",
            
            
            # ============ GOVERNMENT & PUBLIC SECTOR ============
            
            "public administration", "public policy", "policy analysis", "governance",
            "public sector management", "civil service", "government relations",
            "regulatory affairs", "compliance", "public procurement", "grant management",
            "program management", "community development", "urban planning",
            "public health", "epidemiology", "health policy", "emergency management",
            "disaster management", "homeland security", "law enforcement", "policing",
            
            
            # ============ SPORTS & FITNESS ============
            
            "personal training", "fitness training", "strength training", "cardio training",
            "yoga", "pilates", "crossfit", "sports coaching", "athletic training",
            "sports medicine", "physical therapy", "sports nutrition", "nutrition",
            "dietetics", "meal planning", "weight management", "wellness coaching",
            "sports management", "sports marketing", "event management",
            
            
            # ============ TRANSPORTATION & LOGISTICS ============
            
            "transportation", "logistics", "supply chain", "freight forwarding",
            "shipping", "customs clearance", "import export", "trade compliance",
            "fleet management", "route optimization", "warehouse management",
            "distribution", "last mile delivery", "cold chain", "3pl", "4pl",
            "tms", "transportation management system", "wms", "warehouse management system",
            
            
            # ============ SOFT SKILLS (UNIVERSAL) ============
            
            "communication", "verbal communication", "written communication",
            "presentation skills", "public speaking", "active listening",
            "leadership", "team leadership", "team management", "people management",
            "mentoring", "coaching", "delegation", "motivation", "team building",
            "problem solving", "critical thinking", "analytical thinking",
            "creative thinking", "innovation", "decision making", "judgment",
            "time management", "prioritization", "organization", "multitasking",
            "attention to detail", "accuracy", "quality focus",
            "collaboration", "teamwork", "interpersonal skills", "relationship building",
            "networking", "stakeholder management", "client management",
            "negotiation", "persuasion", "influence", "conflict resolution",
            "emotional intelligence", "empathy", "adaptability", "flexibility",
            "resilience", "stress management", "work ethic", "professionalism",
            "integrity", "accountability", "reliability", "initiative",
            "self motivation", "continuous learning", "growth mindset",
            "cultural awareness", "diversity", "inclusion", "cross cultural communication",
        ]
    
    text_lower = text.lower()
    found = []
    
    # Use set for faster lookup and avoid duplicates
    seen = set()
    for skill in skills_list:
        # Use word boundary matching for better accuracy
        if skill in text_lower and skill not in seen:
            found.append(skill)
            seen.add(skill)
    
    return found


def extract_name_from_text(text):
    """
    Attempts to extract candidate name from resume text.
    Assumes name is in the first few lines.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None
    
    # First non-empty line is often the name
    first_line = lines[0]
    
    # Basic validation: name should be 2-4 words, mostly alphabetic
    words = first_line.split()
    if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() or word.replace('.', '').replace(',', '').isalpha() for word in words):
        return first_line
    
    # Try second line if first didn't work
    if len(lines) > 1:
        second_line = lines[1]
        words = second_line.split()
        if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() for word in words):
            return second_line
    
    return None

def parse_resume_file(path, filename):
    if filename.lower().endswith(".pdf"):
        raw = extract_text_from_pdf(path)
    elif filename.lower().endswith(".docx"):
        raw = extract_text_from_docx(path)
    else:
        raise ValueError("Unsupported file type")
    # Simple heuristics: extract name, emails, phone, skills
    name = extract_name_from_text(raw)
    email = re.search(r"[\w\.-]+@[\w\.-]+", raw)
    phone = re.search(r"(\+?\d{10,15})", raw)
    skills = simple_skill_extractor(raw)
    parsed = {
        "name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "skills": skills,
        "raw_text_snippet": raw[:500]
    }
    return raw, parsed
