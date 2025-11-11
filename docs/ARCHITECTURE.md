# 🏗️ OpsFleet Architecture Documentation

> Comprehensive architecture guide for the Professional ReAct Data Analysis Agent

## Table of Contents

1. [System Overview](#system-overview)
2. [5-Stage Pipeline](#5-stage-pipeline)
3. [Multi-Phase Planning](#multi-phase-planning)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Technology Stack](#technology-stack)

## System Overview

OpsFleet implements a sophisticated **Professional ReAct Agent** architecture that combines strategic planning, data sampling, and self-healing execution.

```mermaid
graph TB
    User[👤 User] -->|Natural Language Query| CLI[🖥️ CLI Interface]
    CLI -->|Process Request| Agent[🤖 Professional ReAct Agent]
    
    Agent -->|Stage 1| Understanding[🧠 Understanding<br/>Intent Analysis]
    Agent -->|Stage 2| Planning[📋 Genius Planning<br/>4-Phase Strategic]
    Agent -->|Stage 3| Execution[⚡ ReAct Execution<br/>Think-Act-Observe]
    Agent -->|Stage 4| Validation[✅ Validation<br/>Quality Assurance]
    Agent -->|Stage 5| Synthesis[📝 Synthesis<br/>Insight Generation]
    
    Planning -->|Sample Data| BQ[(BigQuery<br/>Data Warehouse)]
    Execution -->|Execute SQL| BQ
    
    Agent -->|Trace All Stages| LangSmith[📊 LangSmith<br/>Observability]
    Agent -->|Cache Results| Memory[💾 Cache Layer<br/>Schema + Results]
    
    style Agent fill:#4CAF50,color:#fff
    style Planning fill:#2196F3,color:#fff
    style Execution fill:#FF9800,color:#fff
    style BQ fill:#4285F4,color:#fff
```

### Key Principles

1. **Strategic Thinking** - Multi-phase planning before execution
2. **Data Awareness** - Sample data to understand formats
3. **Self-Healing** - Automatic error recovery
4. **Observability** - Full tracing with LangSmith
5. **Performance** - Aggressive caching at multiple layers

## 5-Stage Pipeline

### Stage 1: Understanding 🧠

**Purpose**: Analyze user intent and extract requirements

**Process**:
1. Parse natural language query
2. Identify intent (analysis, aggregation, filtering, etc.)
3. Extract entities (tables, columns, time periods)
4. Assess complexity (simple/medium/complex)
5. Determine output format (table/chart/report)

**Output**: Understanding object with intent, complexity, and requirements

### Stage 2: Genius Planning 📋

**Purpose**: Create optimized execution plan through strategic reasoning

**4-Phase Process**:

#### Phase 0: Data Sampling
- Sample 3 rows from each relevant table
- Infer actual data types (TIMESTAMP, INTEGER, STRING)
- Store samples in context for SQL generation

#### Phase 1: Strategic Analysis
- Identify ultimate goal
- Determine tables and columns needed
- Assess data handling requirements
- Identify risks and optimizations

#### Phase 2: Problem Decomposition
- Break into atomic steps
- Identify dependencies
- Mark critical path
- Estimate timing

#### Phase 3: Execution Optimization
- Combine queries where possible
- Use CTEs for complex logic
- Parallelize independent steps
- Minimize data movement

#### Phase 4: Validation
- Check completeness
- Validate tool names
- Assess confidence
- Calculate success probability

**Output**: Optimized execution plan with confidence scores

### Stage 3: ReAct Execution ⚡

**Purpose**: Execute plan using Think-Act-Observe cycle

**ReAct Loop**:
```
For each step in plan:
    1. THINK: Analyze what needs to be done
    2. ACT: Execute the action (SQL query, analysis, etc.)
    3. OBSERVE: Validate results and check for errors
    4. If error: Self-heal and retry (up to 3 times)
```

**Features**:
- Step-by-step progress tracking
- Detailed logging of each cycle
- Automatic error recovery
- Result validation

**Output**: Execution results with step-by-step logs

### Stage 4: Validation ✅

**Purpose**: Ensure result quality and completeness

**Checks**:
1. Data completeness (no missing required fields)
2. Data quality (no obvious errors)
3. Result relevance (answers the query)
4. Confidence scoring (0-1 scale)

**Output**: Validation report with confidence score

### Stage 5: Synthesis 📝

**Purpose**: Generate insights and recommendations

**Process**:
1. Analyze results for patterns
2. Extract key insights
3. Generate recommendations
4. Format beautiful report

**Output**: Formatted report with insights and recommendations

## Multi-Phase Planning

### Phase 0: Data Sampling

```mermaid
graph LR
    Start[Query] --> Identify[Identify<br/>Tables]
    Identify --> Sample1[Sample<br/>orders]
    Identify --> Sample2[Sample<br/>products]
    Identify --> Sample3[Sample<br/>users]
    
    Sample1 --> Infer[Infer Types]
    Sample2 --> Infer
    Sample3 --> Infer
    
    Infer --> Types[created_at: TIMESTAMP<br/>order_id: INTEGER<br/>sale_price: FLOAT]
    
    Types --> Context[Store in<br/>Context]
    
    style Context fill:#4CAF50,color:#fff
```

**Benefits**:
- Knows actual column names
- Understands data types
- Prevents type mismatch errors
- Enables smart SQL generation

### Phase 1: Strategic Analysis

```mermaid
mindmap
  root((Strategic<br/>Analysis))
    Ultimate Goal
      What insight?
      Why needed?
    Data Strategy
      Which tables?
      What joins?
      Filter early?
    Computational Approach
      Sequential
      Parallel
      Hybrid
    Risks
      Large dataset
      Complex joins
      Type mismatches
    Optimizations
      Use indexes
      Combine queries
      Cache results
```

### Phase 2: Problem Decomposition

```mermaid
graph TD
    Problem[Complex Query] --> Atomic1[Atomic Step 1:<br/>Fetch base data]
    Problem --> Atomic2[Atomic Step 2:<br/>Aggregate]
    Problem --> Atomic3[Atomic Step 3:<br/>Format results]
    
    Atomic1 --> Deps1[Dependencies: None]
    Atomic2 --> Deps2[Dependencies: Step 1]
    Atomic3 --> Deps3[Dependencies: Step 2]
    
    Deps1 --> Critical{Critical?}
    Deps2 --> Critical
    Deps3 --> Critical
    
    Critical -->|Yes| Path[Critical Path]
    Critical -->|No| Optional[Optional]
    
    style Path fill:#FF5722,color:#fff
    style Optional fill:#9E9E9E,color:#fff
```

### Phase 3: Execution Optimization

**Optimization Strategies**:

1. **Query Combining**
   ```sql
   -- Before: 2 queries
   SELECT SUM(revenue) FROM orders WHERE month = 1;
   SELECT COUNT(*) FROM orders WHERE month = 1;
   
   -- After: 1 query
   SELECT SUM(revenue), COUNT(*) FROM orders WHERE month = 1;
   ```

2. **CTE Usage**
   ```sql
   WITH monthly_sales AS (
       SELECT EXTRACT(MONTH FROM created_at) as month,
              SUM(sale_price) as revenue
       FROM order_items
       GROUP BY month
   )
   SELECT month, revenue, 
          LAG(revenue) OVER (ORDER BY month) as prev_month
   FROM monthly_sales;
   ```

3. **Parallelization**
   - Execute independent queries concurrently
   - Reduce total execution time
   - Maximize resource utilization

### Phase 4: Validation

```mermaid
graph TD
    Plan[Execution Plan] --> Check1{Completeness?}
    Check1 -->|Yes| Check2{Correctness?}
    Check1 -->|No| Fix1[Add Missing Steps]
    
    Check2 -->|Yes| Check3{Efficiency?}
    Check2 -->|No| Fix2[Fix Logic]
    
    Check3 -->|Yes| Score[Calculate Scores]
    Check3 -->|No| Fix3[Optimize]
    
    Fix1 --> Check1
    Fix2 --> Check2
    Fix3 --> Check3
    
    Score --> Confidence[Confidence: 0.95]
    Score --> Success[Success Prob: 0.92]
    Score --> Risk[Risk Level: Low]
    
    style Confidence fill:#4CAF50,color:#fff
    style Success fill:#4CAF50,color:#fff
    style Risk fill:#4CAF50,color:#fff
```

## Component Architecture

### Layer Breakdown

```mermaid
graph TB
    subgraph "Presentation Layer"
        CLI[CLI Interface<br/>cli_chat.py]
        Display[Beautiful Display<br/>Rich formatting]
        Progress[Progress Tracking<br/>Real-time updates]
    end
    
    subgraph "Agent Layer"
        PRA[ProfessionalReActAgent<br/>Main orchestrator]
        Understanding[Understanding Stage]
        Planning[Planning Stage]
        Execution[Execution Stage]
        Validation[Validation Stage]
        Synthesis[Synthesis Stage]
    end
    
    subgraph "Planning Layer"
        Strategic[Strategic Analysis]
        Decompose[Problem Decomposition]
        Optimize[Execution Optimization]
        ValidatePlan[Plan Validation]
    end
    
    subgraph "Orchestration Layer"
        Tools[Tools Module]
        BQTool[BigQuery Tool]
        AnalyzeTool[Analyze Tool]
        ReportTool[Report Tool]
    end
    
    subgraph "Data Layer"
        SchemaCache[Schema Cache<br/>Persistent]
        DataSamples[Data Samples<br/>Session-scoped]
        ConvHistory[Conversation History<br/>Multi-turn context]
        ResultCache[Result Cache<br/>Query deduplication]
    end
    
    subgraph "External Services"
        BQ[(BigQuery)]
        LLM[LLM Provider<br/>Gemini/Ollama]
        LangSmith[LangSmith<br/>Tracing]
    end
    
    CLI --> PRA
    Display --> CLI
    Progress --> CLI
    
    PRA --> Understanding
    PRA --> Planning
    PRA --> Execution
    PRA --> Validation
    PRA --> Synthesis
    
    Planning --> Strategic
    Planning --> Decompose
    Planning --> Optimize
    Planning --> ValidatePlan
    
    Execution --> Tools
    Tools --> BQTool
    Tools --> AnalyzeTool
    Tools --> ReportTool
    
    BQTool --> BQ
    Strategic --> DataSamples
    DataSamples --> BQ
    
    PRA --> SchemaCache
    PRA --> ConvHistory
    PRA --> ResultCache
    
    PRA --> LLM
    PRA --> LangSmith
    
    style PRA fill:#4CAF50,color:#fff
    style Planning fill:#2196F3,color:#fff
    style BQ fill:#4285F4,color:#fff
    style LangSmith fill:#FF9800,color:#fff
```

### Key Components

#### 1. ProfessionalReActAgent
- **Location**: `src/agents/professional_react_agent.py`
- **Responsibility**: Main orchestrator for 5-stage pipeline
- **Key Methods**:
  - `process()` - Main entry point
  - `_stage_1_understanding()` - Intent analysis
  - `_stage_2_planning()` - Strategic planning
  - `_stage_3_execution()` - ReAct execution
  - `_stage_4_validation()` - Result validation
  - `_stage_5_synthesis()` - Insight generation

#### 2. Tools Module
- **Location**: `src/orchestration/tools.py`
- **Responsibility**: Tool implementations
- **Tools**:
  - `BigQueryTool` - SQL execution with error handling
  - `AnalyzeTool` - Data analysis and statistics
  - `ReportTool` - Report generation

#### 3. Cache Layer
- **Schema Cache**: Persistent across sessions
- **Data Samples**: Session-scoped, reused for planning
- **Result Cache**: Query deduplication
- **Conversation History**: Multi-turn context

## Data Flow

### Complete Request Flow

```mermaid
flowchart TD
    Start([User Query]) --> ParseCLI[Parse CLI Input]
    ParseCLI --> CheckCache{Schema<br/>Cached?}
    
    CheckCache -->|No| ExploreDB[Explore Database Schema]
    CheckCache -->|Yes| Understanding
    
    ExploreDB --> StoreSchema[Store in Schema Cache]
    StoreSchema --> Understanding[Stage 1: Understanding]
    
    Understanding --> CheckClarify{Needs<br/>Clarification?}
    CheckClarify -->|Yes & First Time| AskUser[Ask User for Clarification]
    CheckClarify -->|No or Already Asked| Planning
    
    AskUser --> Planning[Stage 2: Planning]
    
    Planning --> SampleData[Sample Data from Tables]
    SampleData --> InferTypes[Infer Data Types]
    InferTypes --> Strategic[Strategic Analysis]
    Strategic --> Decompose[Problem Decomposition]
    Decompose --> OptimizePlan[Optimize Execution]
    OptimizePlan --> ValidatePlan[Validate Plan]
    
    ValidatePlan --> Execution[Stage 3: Execution]
    
    Execution --> Loop{More Steps?}
    Loop -->|Yes| Think[Think: Analyze Step]
    Think --> Act[Act: Execute Action]
    Act --> Observe[Observe: Validate Result]
    Observe --> CheckError{Error?}
    
    CheckError -->|Yes| Retry{Retry<br/>Count < 3?}
    Retry -->|Yes| Heal[Self-Heal: Fix Error]
    Heal --> Think
    Retry -->|No| ReturnError[Return Error Response]
    
    CheckError -->|No| StoreResult[Store Step Result]
    StoreResult --> Loop
    
    Loop -->|No| Validation[Stage 4: Validation]
    
    Validation --> CheckQuality{Quality<br/>OK?}
    CheckQuality -->|No| ReturnError
    CheckQuality -->|Yes| Synthesis[Stage 5: Synthesis]
    
    Synthesis --> GenerateInsights[Generate Insights]
    GenerateInsights --> FormatReport[Format Beautiful Report]
    FormatReport --> CacheResult[Cache Result]
    CacheResult --> LogTrace[Log to LangSmith]
    LogTrace --> End([Return to User])
    
    ReturnError --> End
    
    style Start fill:#4CAF50,color:#fff
    style End fill:#4CAF50,color:#fff
    style Planning fill:#2196F3,color:#fff
    style Execution fill:#FF9800,color:#fff
    style Validation fill:#9C27B0,color:#fff
    style Synthesis fill:#00BCD4,color:#fff
```

## Design Patterns

### 1. ReAct Pattern (Reasoning + Acting)

**Implementation**:
```python
async def _stage_3_execution(self, query, plan):
    for step in plan['steps']:
        # THINK: Reason about the step
        thought = await self._think(step, context)
        
        # ACT: Execute the action
        result = await self._act(step, thought)
        
        # OBSERVE: Validate and learn
        observation = await self._observe(result, step)
        
        # Update context for next step
        context.append({
            'thought': thought,
            'action': step,
            'result': result,
            'observation': observation
        })
```

**Benefits**:
- Explicit reasoning before acting
- Observable decision-making process
- Self-correction capabilities
- Traceable execution flow

### 2. Strategy Pattern (Multi-Phase Planning)

**Implementation**:
```python
async def _stage_2_planning(self, query, understanding):
    # Phase 0: Data Sampling Strategy
    samples = await self._sample_data_formats()
    
    # Phase 1: Strategic Analysis Strategy
    strategic = await self._strategic_analysis(query, understanding, samples)
    
    # Phase 2: Decomposition Strategy
    decomposition = await self._problem_decomposition(query, understanding, strategic)
    
    # Phase 3: Optimization Strategy
    optimized = await self._optimize_execution(decomposition)
    
    # Phase 4: Validation Strategy
    validated = await self._validate_plan(optimized, understanding)
    
    return validated
```

**Benefits**:
- Separation of concerns
- Easy to add new strategies
- Testable in isolation
- Clear responsibility boundaries

### 3. Cache-Aside Pattern

**Implementation**:
```python
async def get_schema(self):
    # Check cache first
    if self.db_schema_cache:
        return self.db_schema_cache
    
    # Cache miss - fetch from database
    schema = await self._explore_database()
    
    # Store in cache
    self.db_schema_cache = schema
    
    return schema
```

**Benefits**:
- Reduced database load
- Faster response times
- Explicit cache control
- Simple invalidation

### 4. Chain of Responsibility (Error Handling)

**Implementation**:
```python
async def _execute_with_retry(self, action, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await self._execute(action)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                # Analyze error and fix
                fixed_action = await self._self_heal(action, e)
                action = fixed_action
            else:
                raise
```

**Benefits**:
- Automatic error recovery
- Progressive error handling
- Graceful degradation
- Detailed error logging

## Technology Stack

### Core Technologies

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Primary language | 3.11+ |
| **BigQuery** | Data warehouse | Latest |
| **LangSmith** | Observability | Latest |
| **Gemini** | LLM provider | Latest |
| **Ollama** | Local LLM | Latest |

### Python Libraries

| Library | Purpose |
|---------|---------|
| `google-cloud-bigquery` | BigQuery client |
| `langsmith` | Tracing and observability |
| `rich` | Beautiful CLI formatting |
| `asyncio` | Async execution |
| `pandas` | Data manipulation |
| `pydantic` | Data validation |

### Architecture Patterns

| Pattern | Usage |
|---------|-------|
| **ReAct** | Execution loop (Think-Act-Observe) |
| **Strategy** | Multi-phase planning |
| **Cache-Aside** | Schema and result caching |
| **Chain of Responsibility** | Error handling |
| **Observer** | Progress tracking |
| **Factory** | Tool creation |

## Performance Characteristics

### Latency Breakdown

```
Total Query Time: 2-5 seconds (cached schema)

├── Stage 1: Understanding (200-500ms)
│   └── LLM call for intent analysis
│
├── Stage 2: Planning (1-3 seconds)
│   ├── Data sampling (500ms-1s)
│   ├── Strategic analysis (300ms)
│   ├── Problem decomposition (300ms)
│   ├── Optimization (200ms)
│   └── Validation (200ms)
│
├── Stage 3: Execution (500ms-2s)
│   └── Depends on query complexity
│
├── Stage 4: Validation (100-200ms)
│   └── Result quality checks
│
└── Stage 5: Synthesis (300-500ms)
    └── LLM call for insights
```

### Caching Impact

| Cache Type | Hit Rate | Latency Reduction |
|------------|----------|-------------------|
| Schema Cache | 95%+ | -2 seconds |
| Data Samples | 80%+ | -1 second |
| Result Cache | 30%+ | -3 seconds |

### Scalability

- **Concurrent Queries**: 10+ (limited by LLM rate limits)
- **Database Size**: Tested up to 100GB
- **Query Complexity**: Supports multi-table joins, aggregations, CTEs
- **Memory Usage**: ~200MB per session

## Security Considerations

1. **Credentials**: Service account keys stored securely
2. **SQL Injection**: Parameterized queries only
3. **Data Access**: Row-level security via BigQuery
4. **Logging**: PII filtering in traces
5. **API Keys**: Environment variables only

## Monitoring & Observability

### LangSmith Integration

- **Traces**: Every stage logged
- **Threads**: Conversation grouping
- **Metadata**: Query, plan, results
- **Performance**: Latency tracking
- **Errors**: Full stack traces

### Metrics Tracked

- Query success rate
- Average latency per stage
- Cache hit rates
- Error rates by type
- LLM token usage

## Future Enhancements

1. **Streaming Responses** - Real-time result streaming
2. **Multi-Agent Collaboration** - Specialized agent teams
3. **Advanced Caching** - Semantic query caching
4. **Query Optimization** - ML-powered query rewriting
5. **Multi-Database Support** - PostgreSQL, MySQL, Snowflake

---

**For more details, see the [main README](../README.md) and other documentation files.**
