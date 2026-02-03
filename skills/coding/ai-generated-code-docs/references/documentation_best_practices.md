# Documentation Best Practices for AI-Generated Code

## Principles for Effective Code Documentation

### 1. Clarity Over Completeness
- Focus on WHY rather than WHAT (code already shows what it does)
- Explain design decisions and trade-offs
- Document non-obvious behavior and edge cases

### 2. Target Your Audience
- Assume readers are competent developers
- Focus on what they need to understand and maintain the code
- Include enough context for someone new to the codebase

### 3. Keep Documentation Fresh
- Update docs when code changes
- Remove outdated information immediately
- Mark temporary solutions as such

---

## Identifying Code Complexity Worth Documenting

### High Priority for Documentation

**1. Complex Algorithms**
- Custom sorting, searching, or optimization logic
- Non-standard data structure implementations
- Mathematical computations or formulas

**2. System Integration Points**
- API interactions and data transformations
- Database queries with complex joins or transactions
- External service dependencies

**3. Performance-Critical Code**
- Caching strategies
- Batch processing logic
- Async/concurrent operations

**4. Business Logic**
- Domain-specific rules and constraints
- Workflow orchestration
- State machine implementations

**5. Error Handling & Edge Cases**
- Retry mechanisms
- Fallback strategies
- Validation and sanitization logic

### Lower Priority
- Standard CRUD operations
- Simple getters/setters
- Straightforward utility functions

---

## Writing Clear Technical Explanations

### Pattern: Problem → Solution → Rationale

**Example:**

```
## Challenge: Race Condition in Cache Updates

**Problem**: Multiple concurrent requests could update the same cache entry, 
leading to inconsistent data.

**Solution**: Implemented optimistic locking with version numbers. Each cache 
entry includes a version field that increments on updates.

**Why This Approach**: 
- Tried pessimistic locks first, but caused performance bottlenecks
- Optimistic locking provides better throughput for our read-heavy workload
- Version conflicts are rare (~0.1%) based on our access patterns
```

### Use Concrete Examples

Instead of:
> "This function handles data transformation"

Write:
> "Converts API response from snake_case JSON to camelCase TypeScript objects, 
> while preserving nested structures. Example: `{user_name: 'john'}` becomes 
> `{userName: 'john'}`"

### Explain the "Why" Behind Non-Obvious Code

```python
# Why document this?
def calculate_discount(price, user_tier):
    # Using floor division intentionally to match legacy system behavior
    # Modern pricing would use decimal precision, but changing this would
    # create discrepancies with historical invoices
    return (price * TIER_DISCOUNTS[user_tier]) // 100
```

---

## Language-Specific Documentation Standards

### Python

**Docstrings** (English or Japanese only):
```python
def process_payment(amount: float, currency: str) -> PaymentResult:
    """
    Process a payment transaction with currency conversion.
    
    Args:
        amount: Payment amount in the specified currency
        currency: ISO 4217 currency code (e.g., 'USD', 'EUR', 'JPY')
    
    Returns:
        PaymentResult with transaction ID and status
    
    Raises:
        InvalidCurrencyError: If currency code is not supported
        InsufficientFundsError: If account balance is too low
    
    Note:
        Currency conversion uses mid-market rates updated hourly.
        Transactions are atomic - either fully complete or fully rolled back.
    """
```

### JavaScript/TypeScript

**JSDoc** (English or Japanese only):
```typescript
/**
 * Debounces a function call to reduce execution frequency
 * 
 * @param func - The function to debounce
 * @param wait - Milliseconds to wait before executing
 * @param immediate - Execute on leading edge instead of trailing
 * @returns Debounced version of the function
 * 
 * @example
 * const debouncedSearch = debounce(searchAPI, 300);
 * input.addEventListener('input', debouncedSearch);
 */
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate: boolean = false
): (...args: Parameters<T>) => void {
  // Implementation...
}
```

### Go

**Comments** (English or Japanese only):
```go
// ProcessOrders handles batch order processing with retries.
//
// It processes orders in parallel using a worker pool to maximize throughput
// while respecting rate limits (100 orders/sec per the SLA).
//
// Failed orders are retried with exponential backoff (max 3 attempts).
// After all retries, failures are logged to the dead letter queue.
//
// Returns the number of successfully processed orders and any fatal error
// that stopped processing.
func ProcessOrders(ctx context.Context, orders []Order) (int, error) {
    // Implementation...
}
```

---

## Examples: Good vs. Poor Documentation

### Example 1: API Integration

❌ **Poor**:
```python
# Calls the user API
def get_user(id):
    response = requests.get(f"{API_URL}/users/{id}")
    return response.json()
```

✅ **Good**:
```python
def get_user(user_id: str) -> User:
    """
    Fetch user data from the identity service.
    
    Note: This endpoint caches responses for 5 minutes. If you need
    real-time data, use get_user_realtime() instead, though it's
    significantly slower (500ms vs 50ms average).
    
    Raises:
        UserNotFoundError: If user_id doesn't exist
        ServiceUnavailableError: If identity service is down
    """
    response = requests.get(
        f"{API_URL}/users/{user_id}",
        timeout=10,  # Higher than default to avoid false positives
        headers={"X-Client-ID": CLIENT_ID}
    )
    return User.from_dict(response.json())
```

### Example 2: Complex Business Logic

❌ **Poor**:
```typescript
// Calculate price
function calculatePrice(quantity, type) {
  if (type === 'bulk') {
    return quantity > 100 ? quantity * 9.5 : quantity * 10;
  }
  return quantity * 12;
}
```

✅ **Good**:
```typescript
/**
 * Calculate total price with bulk discount rules
 * 
 * Pricing tiers (as of 2026 pricing policy):
 * - Retail: $12/unit (flat rate)
 * - Bulk (<100 units): $10/unit
 * - Bulk (100+ units): $9.50/unit
 * 
 * Note: The 100-unit threshold aligns with our warehouse pallet size,
 * allowing us to pass shipping savings to customers.
 */
function calculatePrice(quantity: number, type: PriceType): number {
  const RETAIL_PRICE = 12;
  const BULK_PRICE = 10;
  const BULK_DISCOUNT_PRICE = 9.5;
  const BULK_DISCOUNT_THRESHOLD = 100;
  
  if (type === 'bulk') {
    return quantity >= BULK_DISCOUNT_THRESHOLD 
      ? quantity * BULK_DISCOUNT_PRICE 
      : quantity * BULK_PRICE;
  }
  return quantity * RETAIL_PRICE;
}
```

---

## Multi-Language Documentation Guidelines

### Documentation Language Selection

**General Rule**: Match the documentation language to the team/project context:
- **Chinese (中文)**: For Chinese-speaking teams or China-focused projects
- **English**: For international teams or open-source projects
- **Japanese (日本語)**: For Japanese-speaking teams or Japan-focused projects

### Code Comments (English or Japanese ONLY)

```python
# ❌ WRONG - Chinese characters in code comments
# 这个函数计算总价
def calculate_total(items):
    pass

# ✅ CORRECT - English comments
# Calculate total price including tax and discounts
def calculate_total(items):
    pass

# ✅ CORRECT - Japanese comments
# 税金と割引を含む合計金額を計算する
def calculate_total(items):
    pass
```

### Documentation Files (Any Supported Language)

Standalone documentation can use:
- Chinese for `IMPLEMENTATION_ZH.md`
- English for `IMPLEMENTATION.md`
- Japanese for `IMPLEMENTATION_JA.md`

Or use a single bilingual/trilingual file with clear section headers.

---

## Template Usage Guidelines

### When to Use the Full Template

Use the comprehensive template for:
- New features or modules
- Complex systems with multiple components
- Code that will be maintained by different developers
- Projects with high maintenance burden

### When to Use Simplified Documentation

For simpler code, you can omit sections:
- **Skip "Technical Architecture"** for single-file utilities
- **Skip "Technical Challenges"** if implementation is straightforward
- **Skip "Testing"** if tests are self-explanatory

### Customizing the Template

The template is a starting point. Adapt it:
- Add domain-specific sections (e.g., "Security Considerations" for auth code)
- Remove irrelevant sections
- Adjust depth based on complexity

---

## Common Pitfalls to Avoid

### 1. Over-Documenting Obvious Code
```python
# ❌ Don't do this
def add(a, b):
    """Adds two numbers together"""  # Obvious from function name
    return a + b
```

### 2. Outdated Documentation
```python
# ❌ Misleading - code doesn't match comment
# Returns user email address
def get_user(id):
    return User.objects.get(id=id)  # Returns entire User object!
```

### 3. Vague Explanations
```python
# ❌ Too vague
# Handles edge cases
def process_data(data):
    ...

# ✅ Specific
# Handles null values by replacing with default, 
# and trims whitespace from string fields
def process_data(data):
    ...
```

### 4. Documentation Without Context
```python
# ❌ Missing context
MAX_RETRIES = 3  # Maximum retries

# ✅ With context
MAX_RETRIES = 3  # Based on SLA: 3 retries with exponential backoff 
                 # gives 99.9% success rate while staying under 30s timeout
```

---

## Maintenance is Key

Remember: **Documentation is code**. It should be:
- Reviewed like code
- Updated when code changes
- Deleted when no longer needed
- Tested for accuracy

Good documentation makes AI-generated code maintainable. Poor documentation (or no documentation) makes it a liability.
