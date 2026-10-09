from django.core.management.base import BaseCommand
from roadmap.models import Skills, Career, CareerSkill, SkillSubtopic
from .business_data import (
    BUSINESS_SKILLS, BUSINESS_SUBTOPICS, BUSINESS_CAREER_INFO, BUSINESS_CAREER_MAP,
)


# (skill_name, category)
SKILLS = [
    ("Python Basics", "PROGRAMMING"),
    ("Object-Oriented Programming", "PROGRAMMING"),
    ("Data Structures", "DATA_STRUCTURES"),
    ("Algorithms", "ALGORITHMS"),
    ("Git & Version Control", "SOFTWARE_ENGINEERING"),
    ("SQL & Databases", "DATABASE"),
    ("Django Basics", "WEB_DEVELOPMENT"),
    ("Django REST Framework", "WEB_DEVELOPMENT"),
    ("HTML & CSS", "WEB_DEVELOPMENT"),
    ("JavaScript Fundamentals", "WEB_DEVELOPMENT"),
    ("REST API Design", "WEB_DEVELOPMENT"),
    ("Authentication & Security", "CYBER_SECURITY"),
    ("Docker Basics", "DEVOPS"),
    ("CI/CD Pipelines", "DEVOPS"),
    ("Cloud Deployment (AWS/GCP)", "CLOUD_COMPUTING"),
    ("Testing (Unit/Integration)", "SOFTWARE_ENGINEERING"),
    ("Statistics for Data Science", "DATA_SCIENCE"),
    ("NumPy & Pandas", "DATA_SCIENCE"),
    ("Data Cleaning & Preprocessing", "DATA_SCIENCE"),
    ("Exploratory Data Analysis (EDA)", "DATA_SCIENCE"),
    ("Data Visualization & BI", "DATA_SCIENCE"),
    ("Machine Learning Basics", "MACHINE_LEARNING"),
    ("Feature Engineering", "MACHINE_LEARNING"),
    ("Advanced ML & Ensemble Methods", "MACHINE_LEARNING"),
    ("Deep Learning", "ARTIFICIAL_INTELLIGENCE"),
    ("Natural Language Processing (NLP)", "ARTIFICIAL_INTELLIGENCE"),
    ("Generative AI & LLMs", "ARTIFICIAL_INTELLIGENCE"),
    ("Model Deployment (Flask/FastAPI)", "DEVOPS"),
    ("MLOps", "DEVOPS"),
    # Cyber Security
    ("Networking Fundamentals", "NETWORKING"),
    ("Linux & OS Fundamentals", "OS"),
    ("Cryptography Basics", "CYBER_SECURITY"),
    ("Web Application Security", "CYBER_SECURITY"),
    ("Network Security & Firewalls", "CYBER_SECURITY"),
    ("Ethical Hacking & Penetration Testing", "CYBER_SECURITY"),
    ("Security Operations & Incident Response", "CYBER_SECURITY"),
    # Cloud Computing
    ("Cloud Fundamentals", "CLOUD_COMPUTING"),
    ("Infrastructure as Code", "CLOUD_COMPUTING"),
    ("Kubernetes Fundamentals", "CLOUD_COMPUTING"),
    ("Cloud Networking & Security", "CLOUD_COMPUTING"),
    ("Monitoring & Observability", "CLOUD_COMPUTING"),
    # Mobile App Development
    ("Dart & Flutter Basics", "MOBILE_APP_DEVELOPMENT"),
    ("Mobile State Management", "MOBILE_APP_DEVELOPMENT"),
    ("Mobile APIs & Local Storage", "MOBILE_APP_DEVELOPMENT"),
    ("Native Platform Integration", "MOBILE_APP_DEVELOPMENT"),
    ("Mobile App Testing & Debugging", "MOBILE_APP_DEVELOPMENT"),
    ("App Publishing & Deployment", "MOBILE_APP_DEVELOPMENT"),
    # UI/UX Design
    ("Design Fundamentals", "UI_UX_DESIGN"),
    ("User Research", "UI_UX_DESIGN"),
    ("Wireframing & Prototyping", "UI_UX_DESIGN"),
    ("Interaction Design & Accessibility", "UI_UX_DESIGN"),
    ("Design Systems", "UI_UX_DESIGN"),
    ("Usability Testing & Iteration", "UI_UX_DESIGN"),
    # Game Development
    ("C# & Game Scripting Basics", "GAME_DEVELOPMENT"),
    ("Unity Game Engine Fundamentals", "GAME_DEVELOPMENT"),
    ("Game Design Principles", "GAME_DEVELOPMENT"),
    ("Game Graphics & Animation", "GAME_DEVELOPMENT"),
    ("Game Physics & Collision", "GAME_DEVELOPMENT"),
    ("Game Audio & UI", "GAME_DEVELOPMENT"),
    ("Multiplayer & Networking Basics", "GAME_DEVELOPMENT"),
    ("Game Publishing & Optimization", "GAME_DEVELOPMENT"),
    # Data Analyst
    ("Excel for Data Analysis", "DATA_SCIENCE"),
    # Java Developer
    ("Java Basics", "PROGRAMMING"),
    ("Java Backend with Spring Boot", "WEB_DEVELOPMENT"),
    # Backend Developer
    ("Backend System Design Basics", "SOFTWARE_ENGINEERING"),
    # Frontend Developer
    ("React.js Fundamentals", "WEB_DEVELOPMENT"),
    ("Frontend Tooling & State Management", "WEB_DEVELOPMENT"),
    ("Responsive & Accessible UI", "WEB_DEVELOPMENT"),
    # Full Stack Developer (Node.js + React)
    ("Node.js & Express Basics", "WEB_DEVELOPMENT"),
    ("MongoDB & Mongoose Basics", "DATABASE"),
    # AI / Deep Learning
    ("Computer Vision Basics", "ARTIFICIAL_INTELLIGENCE"),
    ("Neural Network Architectures", "ARTIFICIAL_INTELLIGENCE"),
    # Database Manager (DBA)
    ("Database Design & Modeling", "DATABASE"),
    ("Database Administration Basics", "DATABASE"),
]

# skill_name -> list of (group, title) in display order.
# "group" is the major heading (e.g. "Core Python"); title is the sub-major point under it.
SUBTOPICS = {
    "Python Basics": [
        ("Core Python", "Variables"),
        ("Core Python", "Data types"),
        ("Core Python", "Operators"),
        ("Core Python", "if / else"),
        ("Core Python", "for and while loops"),
        ("Core Python", "Functions"),
        ("Core Python", "Lambda functions"),
        ("Core Python", "Lists"),
        ("Core Python", "Tuples"),
        ("Core Python", "Sets"),
        ("Core Python", "Dictionaries"),
        ("Core Python", "Strings"),
        ("Core Python", "List / dictionary comprehension"),
        ("Core Python", "Exception handling"),
        ("Core Python", "File handling"),
        ("Core Python", "Modules and packages"),
    ],
    "Object-Oriented Programming": [
        ("OOP Basics", "Classes and objects"),
        ("OOP Basics", "Constructors (__init__)"),
        ("OOP Basics", "Inheritance"),
        ("OOP Basics", "Polymorphism"),
        ("OOP Basics", "Encapsulation"),
        ("OOP Basics", "Abstraction"),
        ("OOP Basics", "Magic / dunder methods"),
    ],
    "Data Structures": [
        ("Linear Structures", "Arrays"),
        ("Linear Structures", "Linked lists"),
        ("Linear Structures", "Stacks"),
        ("Linear Structures", "Queues"),
        ("Non-linear Structures", "Trees"),
        ("Non-linear Structures", "Graphs"),
        ("Non-linear Structures", "Heaps"),
        ("Non-linear Structures", "Hash tables"),
    ],
    "Algorithms": [
        ("Fundamentals", "Time & space complexity (Big-O)"),
        ("Fundamentals", "Sorting algorithms"),
        ("Fundamentals", "Searching algorithms"),
        ("Problem-solving patterns", "Recursion"),
        ("Problem-solving patterns", "Two pointers"),
        ("Problem-solving patterns", "Sliding window"),
        ("Problem-solving patterns", "Dynamic programming"),
        ("Problem-solving patterns", "Greedy algorithms"),
    ],
    "Git & Version Control": [
        ("Basics", "git init, add, commit"),
        ("Basics", "git push, pull, clone"),
        ("Branching", "git branch and merge"),
        ("Branching", "Resolving merge conflicts"),
        ("Collaboration", "Pull requests"),
        ("Collaboration", ".gitignore and README conventions"),
    ],
    "SQL & Databases": [
        ("Core Querying", "SELECT / WHERE"),
        ("Core Querying", "GROUP BY / HAVING"),
        ("Core Querying", "ORDER BY / DISTINCT / LIMIT"),
        ("Joins", "INNER JOIN"),
        ("Joins", "LEFT / RIGHT JOIN"),
        ("Joins", "FULL JOIN"),
        ("Joins", "SELF JOIN"),
        ("Advanced SQL", "Subqueries"),
        ("Advanced SQL", "CTEs"),
        ("Advanced SQL", "CASE / COALESCE / NULL handling"),
        ("Advanced SQL", "Aggregate, string & date functions"),
        ("Advanced SQL", "Window functions (ROW_NUMBER, RANK, LAG, LEAD)"),
        ("Interview-level SQL", "Nth highest salary"),
        ("Interview-level SQL", "Duplicate records"),
        ("Interview-level SQL", "Running totals & month-over-month analysis"),
    ],
    "HTML & CSS": [
        ("HTML", "Semantic elements"),
        ("HTML", "Forms and inputs"),
        ("CSS", "Box model"),
        ("CSS", "Flexbox"),
        ("CSS", "Grid"),
        ("CSS", "Responsive design"),
    ],
    "JavaScript Fundamentals": [
        ("Core JS", "Variables & data types"),
        ("Core JS", "Functions & scope"),
        ("Core JS", "Arrays & objects"),
        ("Core JS", "DOM manipulation"),
        ("Async JS", "Promises"),
        ("Async JS", "async / await"),
        ("Async JS", "fetch API"),
    ],
    "Django Basics": [
        ("Fundamentals", "Project & app structure"),
        ("Fundamentals", "Models & migrations"),
        ("Fundamentals", "Views & URL routing"),
        ("Fundamentals", "Templates & template tags"),
        ("Admin & Auth", "Django admin"),
        ("Admin & Auth", "Built-in authentication"),
    ],
    "Django REST Framework": [
        ("Core DRF", "Serializers"),
        ("Core DRF", "Generic views & viewsets"),
        ("Core DRF", "Routers"),
        ("Auth & Permissions", "Session & token authentication"),
        ("Auth & Permissions", "Permission classes"),
    ],
    "REST API Design": [
        ("Design", "Resource naming & HTTP verbs"),
        ("Design", "Status codes"),
        ("Design", "Pagination & filtering"),
        ("Design", "Versioning"),
    ],
    "Authentication & Security": [
        ("Auth", "Sessions vs tokens vs JWT"),
        ("Auth", "Password hashing"),
        ("Security", "CSRF & CORS"),
        ("Security", "SQL injection & XSS prevention"),
    ],
    "Docker Basics": [
        ("Fundamentals", "Images vs containers"),
        ("Fundamentals", "Dockerfile"),
        ("Fundamentals", "docker-compose"),
        ("Fundamentals", "Volumes & networking basics"),
    ],
    "CI/CD Pipelines": [
        ("Fundamentals", "What is CI/CD"),
        ("Fundamentals", "GitHub Actions basics"),
        ("Fundamentals", "Automated testing in pipelines"),
        ("Fundamentals", "Deployment automation"),
    ],
    "Cloud Deployment (AWS/GCP)": [
        ("AWS Basics", "EC2"),
        ("AWS Basics", "S3"),
        ("AWS Basics", "IAM"),
        ("AWS Basics", "Lambda basics"),
        ("AWS Basics", "RDS"),
        ("AWS Basics", "CloudWatch basics"),
    ],
    "Testing (Unit/Integration)": [
        ("Fundamentals", "Unit tests"),
        ("Fundamentals", "Integration tests"),
        ("Fundamentals", "Mocking & fixtures"),
        ("Fundamentals", "Test coverage"),
    ],
    "Statistics for Data Science": [
        ("Descriptive Statistics", "Mean, median, mode"),
        ("Descriptive Statistics", "Range, variance, standard deviation"),
        ("Descriptive Statistics", "Percentiles, quartiles, IQR"),
        ("Descriptive Statistics", "Covariance & correlation"),
        ("Probability", "Probability & conditional probability"),
        ("Probability", "Normal distribution"),
        ("Probability", "Binomial distribution"),
        ("Inferential Statistics", "Sampling & population vs sample"),
        ("Inferential Statistics", "Central Limit Theorem"),
        ("Inferential Statistics", "Confidence intervals"),
        ("Inferential Statistics", "Hypothesis testing & p-value"),
        ("Inferential Statistics", "z-test, t-test, ANOVA, chi-square test"),
    ],
    "NumPy & Pandas": [
        ("NumPy", "Arrays & dimensions"),
        ("NumPy", "shape / reshape"),
        ("NumPy", "Indexing & slicing"),
        ("NumPy", "Broadcasting"),
        ("NumPy", "Mathematical operations & aggregation"),
        ("NumPy", "Random numbers"),
        ("Pandas", "Series & DataFrames"),
        ("Pandas", "head / tail / info / describe"),
        ("Pandas", "value_counts / groupby"),
        ("Pandas", "merge / join / concat"),
        ("Pandas", "pivot_table / sort_values"),
    ],
    "Data Cleaning & Preprocessing": [
        ("Missing Values", "isnull / isna"),
        ("Missing Values", "dropna / fillna"),
        ("Duplicates & Types", "duplicated / drop_duplicates"),
        ("Duplicates & Types", "dtypes / astype"),
        ("Outliers", "IQR method"),
        ("Outliers", "Z-score & box plots"),
        ("Transformation", "Encoding (label, one-hot, ordinal)"),
        ("Transformation", "Scaling (Standard, MinMax, Robust)"),
    ],
    "Exploratory Data Analysis (EDA)": [
        ("Workflow", "Understand columns & data types"),
        ("Workflow", "Check missing values & duplicates"),
        ("Workflow", "Statistical summary"),
        ("Analysis", "Univariate analysis"),
        ("Analysis", "Bivariate analysis"),
        ("Analysis", "Multivariate analysis"),
        ("Visualization", "Histogram, box plot, bar chart"),
        ("Visualization", "Scatter plot & heatmap"),
        ("Visualization", "Pair plots"),
    ],
    "Data Visualization & BI": [
        ("Power BI", "Power Query & data cleaning"),
        ("Power BI", "Data modeling & relationships"),
        ("Power BI", "DAX, measures & calculated columns"),
        ("Power BI", "Dashboards, filters & slicers"),
        ("Tableau", "Dimensions & measures"),
        ("Tableau", "Calculated fields & parameters"),
        ("Tableau", "Dashboards & stories"),
    ],
    "Machine Learning Basics": [
        ("Regression", "Linear regression"),
        ("Regression", "Cost function & gradient descent"),
        ("Regression", "R², MAE, MSE, RMSE"),
        ("Regression", "Polynomial, Ridge & Lasso regression"),
        ("Classification", "Logistic regression"),
        ("Classification", "KNN, Decision Tree, Random Forest"),
        ("Classification", "SVM & Naive Bayes"),
        ("Classification", "Confusion matrix"),
        ("Classification", "Accuracy, precision, recall, F1, ROC-AUC"),
        ("Unsupervised Learning", "K-Means clustering"),
        ("Unsupervised Learning", "Hierarchical clustering & DBSCAN"),
        ("Unsupervised Learning", "PCA & dimensionality reduction"),
        ("Core Concepts", "Train/test split & cross-validation"),
        ("Core Concepts", "Overfitting vs underfitting"),
    ],
    "Feature Engineering": [
        ("Feature Creation", "Date/time features"),
        ("Feature Creation", "Log transforms, ratios, binning"),
        ("Categorical Features", "Frequency & target encoding"),
        ("Feature Selection", "Correlation & mutual information"),
        ("Feature Selection", "RFE & feature importance"),
        ("Hyperparameter Tuning", "GridSearchCV / RandomizedSearchCV"),
        ("Hyperparameter Tuning", "Parameters vs hyperparameters"),
    ],
    "Advanced ML & Ensemble Methods": [
        ("Ensemble Learning", "Bagging vs boosting"),
        ("Ensemble Learning", "Random Forest & AdaBoost"),
        ("Ensemble Learning", "XGBoost, LightGBM, CatBoost"),
        ("ML Pipelines", "scikit-learn Pipeline & ColumnTransformer"),
    ],
    "Deep Learning": [
        ("Neural Networks", "Neurons, weights & bias"),
        ("Neural Networks", "Activation functions"),
        ("Neural Networks", "Forward & backpropagation"),
        ("Neural Networks", "Loss functions & optimizers"),
        ("CNNs", "Convolution, ReLU & pooling"),
        ("CNNs", "Image classification projects"),
    ],
    "Natural Language Processing (NLP)": [
        ("Traditional NLP", "Text cleaning & tokenization"),
        ("Traditional NLP", "Stopwords, stemming, lemmatization"),
        ("Traditional NLP", "Bag of Words & TF-IDF"),
        ("Modern NLP", "Word embeddings (Word2Vec)"),
        ("Modern NLP", "Transformers & BERT basics"),
    ],
    "Generative AI & LLMs": [
        ("Foundations", "How LLMs work"),
        ("Foundations", "Prompt engineering"),
        ("Foundations", "Embeddings & vector databases"),
        ("RAG & Agents", "Retrieval-Augmented Generation (RAG)"),
        ("RAG & Agents", "Function / tool calling"),
        ("RAG & Agents", "AI agents & evaluation basics"),
    ],
    "Model Deployment (Flask/FastAPI)": [
        ("Deployment", "Flask / FastAPI basics"),
        ("Deployment", "Exposing a model as a REST API"),
        ("Deployment", "Dockerizing an ML service"),
    ],
    "MLOps": [
        ("Fundamentals", "Model & data versioning"),
        ("Fundamentals", "Experiment tracking (MLflow)"),
        ("Fundamentals", "Model monitoring"),
        ("Fundamentals", "CI/CD for ML"),
    ],

    # ---------------- Cyber Security ----------------
    "Networking Fundamentals": [
        ("Core Concepts", "OSI model"),
        ("Core Concepts", "TCP/IP fundamentals"),
        ("Core Concepts", "Subnetting & IP addressing"),
        ("Core Concepts", "DNS & routing basics"),
        ("Protocols", "HTTP/HTTPS"),
        ("Protocols", "FTP & SSH"),
    ],
    "Linux & OS Fundamentals": [
        ("Linux", "File system & permissions"),
        ("Linux", "Command line basics"),
        ("Linux", "Process & service management"),
        ("Windows", "Windows fundamentals"),
        ("Windows", "User & group management"),
    ],
    "Cryptography Basics": [
        ("Encryption", "Symmetric vs asymmetric encryption"),
        ("Encryption", "Hashing algorithms"),
        ("Encryption", "Digital signatures & certificates"),
        ("Encryption", "SSL/TLS fundamentals"),
    ],
    "Web Application Security": [
        ("OWASP Top 10", "Injection attacks (SQLi, XSS)"),
        ("OWASP Top 10", "Broken authentication"),
        ("OWASP Top 10", "CSRF & security misconfiguration"),
        ("Defense", "Input validation & sanitization"),
        ("Defense", "Security headers"),
    ],
    "Network Security & Firewalls": [
        ("Perimeter Defense", "Firewalls"),
        ("Perimeter Defense", "IDS/IPS"),
        ("Perimeter Defense", "VPNs"),
        ("Perimeter Defense", "Network segmentation"),
        ("Recon", "Port scanning basics"),
    ],
    "Ethical Hacking & Penetration Testing": [
        ("Methodology", "Reconnaissance"),
        ("Methodology", "Vulnerability scanning"),
        ("Methodology", "Exploitation basics"),
        ("Methodology", "Reporting & remediation"),
        ("Tools", "Nmap, Burp Suite & Metasploit basics"),
    ],
    "Security Operations & Incident Response": [
        ("SOC", "SIEM basics"),
        ("SOC", "Log analysis"),
        ("Incident Response", "IR lifecycle"),
        ("Incident Response", "Threat intelligence basics"),
    ],

    # ---------------- Cloud Computing ----------------
    "Cloud Fundamentals": [
        ("Core Concepts", "What is cloud computing"),
        ("Core Concepts", "IaaS vs PaaS vs SaaS"),
        ("Core Concepts", "Public, private & hybrid cloud"),
        ("Core Concepts", "Shared responsibility model"),
        ("Core Concepts", "Cloud pricing basics"),
    ],
    "Infrastructure as Code": [
        ("IaC", "IaC principles"),
        ("IaC", "Terraform basics"),
        ("IaC", "CloudFormation basics"),
    ],
    "Kubernetes Fundamentals": [
        ("Core Concepts", "Pods & deployments"),
        ("Core Concepts", "Services & networking"),
        ("Core Concepts", "ConfigMaps & secrets"),
        ("Core Concepts", "Scaling basics"),
    ],
    "Cloud Networking & Security": [
        ("Networking", "VPCs & subnets"),
        ("Networking", "Load balancers"),
        ("Security", "Security groups"),
        ("Security", "IAM policies"),
    ],
    "Monitoring & Observability": [
        ("Observability", "CloudWatch / Stackdriver basics"),
        ("Observability", "Centralized logging"),
        ("Observability", "Alerting"),
        ("Observability", "Cost monitoring"),
    ],

    # ---------------- Mobile App Development ----------------
    "Dart & Flutter Basics": [
        ("Dart", "Dart syntax & basics"),
        ("Flutter", "Stateless & stateful widgets"),
        ("Flutter", "Layouts (Row/Column/Stack)"),
        ("Flutter", "Navigation & routing"),
    ],
    "Mobile State Management": [
        ("State Management", "setState basics"),
        ("State Management", "Provider"),
        ("State Management", "Bloc pattern basics"),
        ("State Management", "Riverpod overview"),
    ],
    "Mobile APIs & Local Storage": [
        ("Networking", "HTTP requests in Flutter"),
        ("Networking", "JSON parsing"),
        ("Storage", "SharedPreferences"),
        ("Storage", "SQLite / local DB basics"),
    ],
    "Native Platform Integration": [
        ("Device Features", "Permissions handling"),
        ("Device Features", "Camera & media access"),
        ("Device Features", "Push notifications"),
        ("Device Features", "Platform channels basics"),
    ],
    "Mobile App Testing & Debugging": [
        ("Testing", "Widget testing"),
        ("Testing", "Debugging tools"),
        ("Testing", "Performance profiling"),
    ],
    "App Publishing & Deployment": [
        ("Release", "App signing"),
        ("Release", "Play Store submission"),
        ("Release", "App Store submission basics"),
        ("Release", "CI/CD for mobile basics"),
    ],

    # ---------------- UI/UX Design ----------------
    "Design Fundamentals": [
        ("Visual Design", "Color theory"),
        ("Visual Design", "Typography basics"),
        ("Visual Design", "Layout & grid systems"),
        ("Visual Design", "Visual hierarchy"),
    ],
    "User Research": [
        ("Research Methods", "User interviews"),
        ("Research Methods", "Personas"),
        ("Research Methods", "Journey mapping"),
        ("Research Methods", "Usability testing basics"),
    ],
    "Wireframing & Prototyping": [
        ("Process", "Low-fidelity wireframes"),
        ("Process", "High-fidelity mockups"),
        ("Process", "Interactive prototypes"),
        ("Tools", "Figma basics"),
    ],
    "Interaction Design & Accessibility": [
        ("Interaction", "Micro-interactions"),
        ("Interaction", "Navigation patterns"),
        ("Accessibility", "Accessibility basics (WCAG)"),
        ("Accessibility", "Responsive design principles"),
    ],
    "Design Systems": [
        ("System Design", "Component libraries"),
        ("System Design", "Design tokens"),
        ("System Design", "Style guides"),
        ("System Design", "Consistency & reuse"),
    ],
    "Usability Testing & Iteration": [
        ("Validation", "A/B testing basics"),
        ("Validation", "Heuristic evaluation"),
        ("Validation", "Gathering feedback"),
        ("Validation", "Iterating on designs"),
    ],

    # ---------------- Game Development ----------------
    "C# & Game Scripting Basics": [
        ("C# Basics", "Variables, types & control flow"),
        ("C# Basics", "Classes & OOP in C#"),
        ("C# Basics", "Coroutines & events"),
    ],
    "Unity Game Engine Fundamentals": [
        ("Unity Editor", "Editor basics & workflow"),
        ("Unity Editor", "GameObjects & components"),
        ("Unity Editor", "Scenes & prefabs"),
        ("Unity Editor", "Physics basics"),
    ],
    "Game Design Principles": [
        ("Design", "Game loops"),
        ("Design", "Core mechanics design"),
        ("Design", "Level design basics"),
        ("Design", "Game balancing"),
    ],
    "Game Graphics & Animation": [
        ("Graphics", "Sprites & spritesheets"),
        ("Graphics", "Animation basics"),
        ("Graphics", "Particle effects"),
        ("Graphics", "Shaders overview"),
    ],
    "Game Physics & Collision": [
        ("Physics", "Colliders & triggers"),
        ("Physics", "Rigidbody physics"),
        ("Physics", "Raycasting basics"),
    ],
    "Game Audio & UI": [
        ("Audio", "Sound effects & music integration"),
        ("UI", "In-game UI/HUD design"),
        ("UI", "Menus & settings"),
    ],
    "Multiplayer & Networking Basics": [
        ("Networking", "Client-server basics"),
        ("Networking", "Netcode overview"),
        ("Networking", "Synchronization challenges"),
    ],
    "Game Publishing & Optimization": [
        ("Release", "Build & export"),
        ("Release", "Performance optimization"),
        ("Release", "Platform-specific considerations"),
    ],

    # ---------------- Data Analyst ----------------
    "Excel for Data Analysis": [
        ("Core Excel", "Formulas & functions"),
        ("Core Excel", "Pivot tables"),
        ("Core Excel", "VLOOKUP / XLOOKUP"),
        ("Core Excel", "Conditional formatting"),
        ("Core Excel", "Data validation"),
    ],

    # ---------------- Java Developer ----------------
    "Java Basics": [
        ("Core Java", "Variables, types & control flow"),
        ("Core Java", "OOP in Java"),
        ("Core Java", "Collections framework"),
        ("Core Java", "Exception handling"),
    ],
    "Java Backend with Spring Boot": [
        ("Spring Boot", "Spring Boot basics"),
        ("Spring Boot", "REST controllers"),
        ("Spring Boot", "Dependency injection"),
        ("Spring Boot", "Spring Data JPA"),
        ("Spring Boot", "Spring Security basics"),
    ],

    # ---------------- Backend Developer ----------------
    "Backend System Design Basics": [
        ("System Design", "Caching strategies"),
        ("System Design", "Load balancing"),
        ("System Design", "Database indexing"),
        ("System Design", "Message queues basics"),
        ("System Design", "API rate limiting"),
    ],

    # ---------------- Frontend Developer ----------------
    "React.js Fundamentals": [
        ("React Basics", "Components & JSX"),
        ("React Basics", "Props & state"),
        ("React Basics", "Hooks (useState / useEffect)"),
        ("React Basics", "Event handling"),
        ("React Basics", "Conditional rendering & lists"),
    ],
    "Frontend Tooling & State Management": [
        ("Tooling", "npm / yarn basics"),
        ("Tooling", "Bundlers (Vite/Webpack overview)"),
        ("Routing & State", "React Router"),
        ("Routing & State", "Context API / Redux basics"),
    ],
    "Responsive & Accessible UI": [
        ("Layout", "CSS Flexbox & Grid mastery"),
        ("Layout", "Responsive breakpoints"),
        ("Accessibility", "Accessibility basics (ARIA)"),
        ("Accessibility", "Cross-browser testing"),
    ],

    # ---------------- Full Stack (Node.js + React) ----------------
    "Node.js & Express Basics": [
        ("Node.js", "Node.js runtime & modules"),
        ("Express", "Express routing & middleware"),
        ("Express", "Building REST APIs with Express"),
        ("Express", "Error handling"),
    ],
    "MongoDB & Mongoose Basics": [
        ("MongoDB", "NoSQL vs SQL"),
        ("MongoDB", "CRUD operations"),
        ("Mongoose", "Schemas & models"),
        ("Mongoose", "Aggregation basics"),
    ],

    # ---------------- AI / Deep Learning ----------------
    "Computer Vision Basics": [
        ("Vision", "Image processing fundamentals"),
        ("Vision", "CNN architectures for vision"),
        ("Vision", "Object detection basics"),
        ("Vision", "OpenCV basics"),
    ],
    "Neural Network Architectures": [
        ("Architectures", "CNNs deep dive"),
        ("Architectures", "RNNs & LSTMs"),
        ("Architectures", "Transformers architecture"),
        ("Architectures", "Transfer learning"),
    ],

    # ---------------- Database Manager (DBA) ----------------
    "Database Design & Modeling": [
        ("Modeling", "ER diagrams"),
        ("Modeling", "Normalization"),
        ("Modeling", "Schema design"),
        ("Modeling", "Data integrity constraints"),
    ],
    "Database Administration Basics": [
        ("Administration", "Installation & configuration"),
        ("Administration", "User & role management"),
        ("Administration", "Indexing strategies"),
        ("Administration", "Query optimization"),
        ("Administration", "Backup & recovery"),
    ],
}

# (career_key, [(skill_name, level, priority), ...])
CAREER_MAP = {
    "PROGRAMMING": [
        ("Python Basics", "BEGINNER", 1),
        ("Object-Oriented Programming", "BEGINNER", 2),
        ("Data Structures", "INTERMEDIATE", 3),
        ("Algorithms", "INTERMEDIATE", 4),
        ("Git & Version Control", "BEGINNER", 5),
        ("Testing (Unit/Integration)", "INTERMEDIATE", 6),
    ],
    "WEB_DEVELOPMENT": [
        ("Python Basics", "BEGINNER", 1),
        ("HTML & CSS", "BEGINNER", 2),
        ("JavaScript Fundamentals", "BEGINNER", 3),
        ("Git & Version Control", "BEGINNER", 4),
        ("SQL & Databases", "INTERMEDIATE", 5),
        ("Django Basics", "INTERMEDIATE", 6),
        ("Django REST Framework", "INTERMEDIATE", 7),
        ("REST API Design", "INTERMEDIATE", 8),
        ("Authentication & Security", "INTERMEDIATE", 9),
        ("Docker Basics", "ADVANCED", 10),
        ("Cloud Deployment (AWS/GCP)", "ADVANCED", 11),
    ],
    "DATA_SCIENCE": [
        ("Python Basics", "BEGINNER", 1),
        ("SQL & Databases", "INTERMEDIATE", 2),
        ("Statistics for Data Science", "INTERMEDIATE", 3),
        ("NumPy & Pandas", "INTERMEDIATE", 4),
        ("Data Cleaning & Preprocessing", "INTERMEDIATE", 5),
        ("Exploratory Data Analysis (EDA)", "INTERMEDIATE", 6),
        ("Data Visualization & BI", "INTERMEDIATE", 7),
        ("Machine Learning Basics", "ADVANCED", 8),
        ("Feature Engineering", "ADVANCED", 9),
        ("Advanced ML & Ensemble Methods", "ADVANCED", 10),
        ("Deep Learning", "ADVANCED", 11),
        ("Natural Language Processing (NLP)", "ADVANCED", 12),
        ("Generative AI & LLMs", "ADVANCED", 13),
        ("Model Deployment (Flask/FastAPI)", "ADVANCED", 14),
        ("MLOps", "ADVANCED", 15),
    ],
    "DEVOPS": [
        ("Git & Version Control", "BEGINNER", 1),
        ("Docker Basics", "INTERMEDIATE", 2),
        ("CI/CD Pipelines", "INTERMEDIATE", 3),
        ("Cloud Deployment (AWS/GCP)", "ADVANCED", 4),
        ("Authentication & Security", "INTERMEDIATE", 5),
    ],
    "MACHINE_LEARNING": [
        ("Python Basics", "BEGINNER", 1),
        ("Statistics for Data Science", "INTERMEDIATE", 2),
        ("NumPy & Pandas", "INTERMEDIATE", 3),
        ("Machine Learning Basics", "ADVANCED", 4),
        ("Feature Engineering", "ADVANCED", 5),
        ("Advanced ML & Ensemble Methods", "ADVANCED", 6),
        ("Deep Learning", "ADVANCED", 7),
        ("Natural Language Processing (NLP)", "ADVANCED", 8),
        ("Model Deployment (Flask/FastAPI)", "ADVANCED", 9),
        ("MLOps", "ADVANCED", 10),
    ],
    "CYBER_SECURITY": [
        ("Networking Fundamentals", "BEGINNER", 1),
        ("Linux & OS Fundamentals", "BEGINNER", 2),
        ("Cryptography Basics", "INTERMEDIATE", 3),
        ("Authentication & Security", "INTERMEDIATE", 4),
        ("Web Application Security", "INTERMEDIATE", 5),
        ("Network Security & Firewalls", "INTERMEDIATE", 6),
        ("Ethical Hacking & Penetration Testing", "ADVANCED", 7),
        ("Security Operations & Incident Response", "ADVANCED", 8),
    ],
    "CLOUD_COMPUTING": [
        ("Cloud Fundamentals", "BEGINNER", 1),
        ("Git & Version Control", "BEGINNER", 2),
        ("Docker Basics", "INTERMEDIATE", 3),
        ("Cloud Deployment (AWS/GCP)", "INTERMEDIATE", 4),
        ("Cloud Networking & Security", "INTERMEDIATE", 5),
        ("Infrastructure as Code", "ADVANCED", 6),
        ("Kubernetes Fundamentals", "ADVANCED", 7),
        ("CI/CD Pipelines", "ADVANCED", 8),
        ("Monitoring & Observability", "ADVANCED", 9),
    ],
    "MOBILE_APP_DEVELOPMENT": [
        ("Object-Oriented Programming", "BEGINNER", 1),
        ("Git & Version Control", "BEGINNER", 2),
        ("Dart & Flutter Basics", "BEGINNER", 3),
        ("Mobile State Management", "INTERMEDIATE", 4),
        ("Mobile APIs & Local Storage", "INTERMEDIATE", 5),
        ("Native Platform Integration", "INTERMEDIATE", 6),
        ("Mobile App Testing & Debugging", "ADVANCED", 7),
        ("App Publishing & Deployment", "ADVANCED", 8),
    ],
    "UI_UX_DESIGN": [
        ("Design Fundamentals", "BEGINNER", 1),
        ("User Research", "BEGINNER", 2),
        ("Wireframing & Prototyping", "INTERMEDIATE", 3),
        ("Interaction Design & Accessibility", "INTERMEDIATE", 4),
        ("Design Systems", "ADVANCED", 5),
        ("Usability Testing & Iteration", "ADVANCED", 6),
    ],
    "GAME_DEVELOPMENT": [
        ("C# & Game Scripting Basics", "BEGINNER", 1),
        ("Git & Version Control", "BEGINNER", 2),
        ("Unity Game Engine Fundamentals", "BEGINNER", 3),
        ("Game Design Principles", "INTERMEDIATE", 4),
        ("Game Graphics & Animation", "INTERMEDIATE", 5),
        ("Game Physics & Collision", "INTERMEDIATE", 6),
        ("Game Audio & UI", "INTERMEDIATE", 7),
        ("Multiplayer & Networking Basics", "ADVANCED", 8),
        ("Game Publishing & Optimization", "ADVANCED", 9),
    ],
    "DATA_ANALYST": [
        ("Python Basics", "BEGINNER", 1),
        ("Excel for Data Analysis", "BEGINNER", 2),
        ("SQL & Databases", "INTERMEDIATE", 3),
        ("Statistics for Data Science", "INTERMEDIATE", 4),
        ("NumPy & Pandas", "INTERMEDIATE", 5),
        ("Data Cleaning & Preprocessing", "INTERMEDIATE", 6),
        ("Exploratory Data Analysis (EDA)", "INTERMEDIATE", 7),
        ("Data Visualization & BI", "ADVANCED", 8),
    ],
    "JAVA_DEVELOPER": [
        ("Java Basics", "BEGINNER", 1),
        ("Object-Oriented Programming", "BEGINNER", 2),
        ("Git & Version Control", "BEGINNER", 3),
        ("SQL & Databases", "INTERMEDIATE", 4),
        ("Java Backend with Spring Boot", "INTERMEDIATE", 5),
        ("REST API Design", "INTERMEDIATE", 6),
        ("Authentication & Security", "INTERMEDIATE", 7),
        ("Testing (Unit/Integration)", "INTERMEDIATE", 8),
        ("Docker Basics", "ADVANCED", 9),
        ("Cloud Deployment (AWS/GCP)", "ADVANCED", 10),
    ],
    "BACKEND_DEVELOPER": [
        ("Python Basics", "BEGINNER", 1),
        ("Object-Oriented Programming", "BEGINNER", 2),
        ("Git & Version Control", "BEGINNER", 3),
        ("SQL & Databases", "INTERMEDIATE", 4),
        ("Django Basics", "INTERMEDIATE", 5),
        ("Django REST Framework", "INTERMEDIATE", 6),
        ("REST API Design", "INTERMEDIATE", 7),
        ("Authentication & Security", "INTERMEDIATE", 8),
        ("Backend System Design Basics", "ADVANCED", 9),
        ("Testing (Unit/Integration)", "ADVANCED", 10),
        ("Docker Basics", "ADVANCED", 11),
        ("Cloud Deployment (AWS/GCP)", "ADVANCED", 12),
    ],
    "FRONTEND_DEVELOPER": [
        ("HTML & CSS", "BEGINNER", 1),
        ("JavaScript Fundamentals", "BEGINNER", 2),
        ("Git & Version Control", "BEGINNER", 3),
        ("React.js Fundamentals", "INTERMEDIATE", 4),
        ("Responsive & Accessible UI", "INTERMEDIATE", 5),
        ("Frontend Tooling & State Management", "ADVANCED", 6),
        ("REST API Design", "ADVANCED", 7),
        ("Testing (Unit/Integration)", "ADVANCED", 8),
    ],
    "FULL_STACK_DEVELOPER": [
        ("HTML & CSS", "BEGINNER", 1),
        ("JavaScript Fundamentals", "BEGINNER", 2),
        ("Git & Version Control", "BEGINNER", 3),
        ("React.js Fundamentals", "INTERMEDIATE", 4),
        ("Node.js & Express Basics", "INTERMEDIATE", 5),
        ("MongoDB & Mongoose Basics", "INTERMEDIATE", 6),
        ("REST API Design", "INTERMEDIATE", 7),
        ("Frontend Tooling & State Management", "ADVANCED", 8),
        ("Authentication & Security", "ADVANCED", 9),
        ("Docker Basics", "ADVANCED", 10),
        ("Cloud Deployment (AWS/GCP)", "ADVANCED", 11),
    ],
    "ARTIFICIAL_INTELLIGENCE": [
        ("Python Basics", "BEGINNER", 1),
        ("Statistics for Data Science", "INTERMEDIATE", 2),
        ("NumPy & Pandas", "INTERMEDIATE", 3),
        ("Machine Learning Basics", "ADVANCED", 4),
        ("Deep Learning", "ADVANCED", 5),
        ("Computer Vision Basics", "ADVANCED", 6),
        ("Natural Language Processing (NLP)", "ADVANCED", 7),
        ("Generative AI & LLMs", "ADVANCED", 8),
        ("Model Deployment (Flask/FastAPI)", "ADVANCED", 9),
    ],
    "DEEP_LEARNING": [
        ("Python Basics", "BEGINNER", 1),
        ("NumPy & Pandas", "INTERMEDIATE", 2),
        ("Machine Learning Basics", "INTERMEDIATE", 3),
        ("Deep Learning", "ADVANCED", 4),
        ("Neural Network Architectures", "ADVANCED", 5),
        ("Computer Vision Basics", "ADVANCED", 6),
        ("Natural Language Processing (NLP)", "ADVANCED", 7),
        ("Model Deployment (Flask/FastAPI)", "ADVANCED", 8),
    ],
    "DATABASE": [
        ("SQL & Databases", "BEGINNER", 1),
        ("Database Design & Modeling", "INTERMEDIATE", 2),
        ("Database Administration Basics", "INTERMEDIATE", 3),
        ("Linux & OS Fundamentals", "INTERMEDIATE", 4),
        ("Cloud Deployment (AWS/GCP)", "ADVANCED", 5),
    ],
}


class Command(BaseCommand):
    help = "Seed the database with sample Skills, Subtopics, Careers, and CareerSkill requirements (technical + business)."

    def handle(self, *args, **options):
        skill_objs = {}
        for name, category in SKILLS:
            skill, _ = Skills.objects.get_or_create(name=name, defaults={"category": category})
            skill_objs[name] = skill

        # Business / non-technical skills carry a plain-language description and realistic duration.
        for name, category, days, description in BUSINESS_SKILLS:
            skill, _ = Skills.objects.update_or_create(
                name=name,
                defaults={"category": category, "typical_duration_days": days, "description": description},
            )
            skill_objs[name] = skill
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(skill_objs)} skills."))

        all_subtopics = {**SUBTOPICS, **BUSINESS_SUBTOPICS}
        subtopic_count = 0
        for skill_name, topics in all_subtopics.items():
            skill = skill_objs.get(skill_name)
            if not skill:
                continue
            for order, (group, title) in enumerate(topics, start=1):
                SkillSubtopic.objects.get_or_create(
                    skill=skill, title=title,
                    defaults={"group": group, "order": order}
                )
                subtopic_count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {subtopic_count} subtopics."))

        all_careers = {**CAREER_MAP, **BUSINESS_CAREER_MAP}
        for career_key, requirements in all_careers.items():
            career, _ = Career.objects.get_or_create(name=career_key)
            info = BUSINESS_CAREER_INFO.get(career_key)
            if info:
                career.stream = "BUSINESS"
                career.requires_coding = False
                career.tagline = info["tagline"]
                career.description = info["description"]
                career.example_roles = info["example_roles"]
                career.save()
            for skill_name, level, priority in requirements:
                CareerSkill.objects.get_or_create(
                    career=career,
                    skill=skill_objs[skill_name],
                    defaults={"required_level": level, "priority": priority}
                )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(all_careers)} career paths with requirements."))
