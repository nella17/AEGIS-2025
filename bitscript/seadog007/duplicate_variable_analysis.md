# Duplicate Variable Declaration - Behavior Analysis

## Test Results

**Input:**
```bitscript
int x = 1;
int x = 2;
int x = 3;
int x = 4;
int x = 5;
print(x);
```

**Output:** `5`

## What's Happening

### Step-by-Step Execution

1. **`int x = 1;`**
   - `add_variable("x", 0)` → Creates entry #1 in variable table
   - `get_variable("x")` → Returns entry #1
   - Evaluates `1` → `v5 = 1`
   - Sets `entry#1.value_ptr = 1`

2. **`int x = 2;`**
   - `add_variable("x", 0)` → Creates entry #2 in variable table (LEAKED!)
   - `get_variable("x")` → Returns entry #1 (first match)
   - Evaluates `2` → `v5 = 2`
   - Sets `entry#1.value_ptr = 2` (overwrites entry #1)

3. **`int x = 3;`**
   - `add_variable("x", 0)` → Creates entry #3 in variable table (LEAKED!)
   - `get_variable("x")` → Returns entry #1 (first match)
   - Evaluates `3` → `v5 = 3`
   - Sets `entry#1.value_ptr = 3` (overwrites entry #1)

4. **`int x = 4;`**
   - `add_variable("x", 0)` → Creates entry #4 in variable table (LEAKED!)
   - `get_variable("x")` → Returns entry #1 (first match)
   - Evaluates `4` → `v5 = 4`
   - Sets `entry#1.value_ptr = 4` (overwrites entry #1)

5. **`int x = 5;`**
   - `add_variable("x", 0)` → Creates entry #5 in variable table (LEAKED!)
   - `get_variable("x")` → Returns entry #1 (first match)
   - Evaluates `5` → `v5 = 5`
   - Sets `entry#1.value_ptr = 5` (overwrites entry #1)

6. **`print(x);`**
   - `get_variable("x")` → Returns entry #1
   - Prints value: `5`

## Memory Leak Confirmed

**Result:**
- Entry #1: Active, value = 5
- Entry #2: LEAKED (64 bytes)
- Entry #3: LEAKED (64 bytes)
- Entry #4: LEAKED (64 bytes)
- Entry #5: LEAKED (64 bytes)

**Total Leaked:** 256 bytes (4 × 64 bytes)

## Variable Table State

After all declarations, the variable table linked list looks like:
```
[Entry #1: name="x", value=5] ← Active (returned by get_variable)
  ↓ next
[Entry #2: name="x", value=undefined] ← LEAKED
  ↓ next
[Entry #3: name="x", value=undefined] ← LEAKED
  ↓ next
[Entry #4: name="x", value=undefined] ← LEAKED
  ↓ next
[Entry #5: name="x", value=undefined] ← LEAKED
```

## Exploitation Potential

### 1. Memory Exhaustion
- Each duplicate declaration leaks 64 bytes
- Can be repeated to exhaust memory
- Limited by `var_table_count > 127` check (max 128 variables)

### 2. Variable Table Corruption
- Multiple entries with same name cause confusion
- If we can corrupt linked list pointers, might access leaked entries
- Could combine with bitmap overflow to modify variable table structure

### 3. Type Confusion
```bitscript
int x = 42;
string x = "hello";
```
- Entry #1: type=int, value=42
- Entry #2: type=string, value="hello" (LEAKED)
- `get_variable("x")` returns entry #1 (int)
- But entry #2 (string) exists in memory
- If we can access entry #2, we get type confusion

### 4. Combined with Bitmap Overflow
- Use bitmap overflow to corrupt variable table entries
- Modify `next` pointer of entry #1 to point to entry #2
- Then `get_variable` might return entry #2 instead
- This could lead to type confusion or use-after-free

## Severity Assessment

**Current Severity: MEDIUM**
- Memory leak confirmed
- Limited impact on its own (just leaks memory)
- Could be more serious if combined with other vulnerabilities

**Potential Severity: HIGH**
- If combined with bitmap overflow for variable table corruption
- Could lead to type confusion, use-after-free, or RCE

