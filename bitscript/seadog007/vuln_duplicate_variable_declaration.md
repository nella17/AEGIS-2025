# Vulnerability: Duplicate Variable Declaration (0x404ca2)

## Location
`eval_statement` function, DECLARATION case (case 0xF), line 24 (address 0x404ca2)

## The Vulnerability

**Code Flow:**
```c
case 0xF:  // DECLARATION
  v7 = *(_DWORD *)(v2 + 64);  // Get type from AST node
  add_variable(*(_QWORD *)(v2 + 72), v7);  // <-- 0x404ca2: Adds variable WITHOUT checking if it exists!
  v6 = get_variable(*(_QWORD *)(v2 + 72));  // Gets variable (returns FIRST match)
  // ... rest of code
```

## The Problem

1. **No Duplicate Check**: `add_variable` is called **BEFORE** checking if the variable already exists
2. **Multiple Entries**: If a variable is declared twice, both entries exist in the variable table
3. **get_variable Returns First Match**: `get_variable` searches from the head and returns the **first** variable with that name
4. **Memory Leak**: The new variable entry is added but never used if an old one exists
5. **Potential Use-After-Free**: If the old variable is freed/deleted, the new entry might still reference freed memory

## Analysis of add_variable

```c
__int64 __fastcall add_variable(const char *a1, int a2)
{
  // No check for existing variable!
  dest = (char *)malloc(0x40u);  // Allocates new variable entry
  strncpy(dest, a1, 0x1Fu);      // Copies name
  dest[31] = 0;
  *((_DWORD *)dest + 8) = a2;    // Sets type
  // Adds to linked list...
  return (unsigned int)++var_table_count;
}
```

**Issues:**
- No check if variable with same name already exists
- Always allocates new memory
- Always increments count
- Adds to linked list unconditionally

## Exploitation Scenarios

### Scenario 1: Memory Leak
```bitscript
int x = 42;
int x = 100;  // Declares x again
// Result: Two entries for "x" in variable table
// First entry (x=42) is used, second entry (x=100) is leaked
```

### Scenario 2: Variable Table Corruption
```bitscript
int x = 42;
string x = "hello";  // Different type!
// Result: Two entries for "x" with different types
// get_variable returns first one (int), but second one (string) exists
// Type confusion potential
```

### Scenario 3: Use-After-Free (if combined with delete)
```bitscript
int x = 42;
delete(x);
int x = 100;  // Redeclares after delete
// First entry is freed, but new entry is added
// If get_variable somehow returns freed entry → UAF
```

## Impact

**Severity: MEDIUM to HIGH**

1. **Memory Leak**: Each duplicate declaration leaks 0x40 bytes (64 bytes)
2. **Variable Table Corruption**: Multiple entries with same name cause confusion
3. **Potential Type Confusion**: Different types for same name
4. **Use-After-Free Risk**: If combined with other vulnerabilities

## Proof of Concept

```bitscript
int x = 1;
int x = 2;
int x = 3;
int x = 4;
int x = 5;
// Each declaration adds a new entry to variable table
// Only the first one is accessible via get_variable
// Others are leaked
```

## Fix

**Before calling `add_variable`, check if variable exists:**

```c
case 0xF:
  v7 = *(_DWORD *)(v2 + 64);
  v6 = get_variable(*(_QWORD *)(v2 + 72));  // Check first!
  if (v6) {
    // Variable exists - either error or handle overwrite
    fprintf(stderr, "Variable %s already declared\n", *(_QWORD *)(v2 + 72));
    exit(1);
  }
  add_variable(*(_QWORD *)(v2 + 72), v7);  // Now safe to add
  v6 = get_variable(*(_QWORD *)(v2 + 72));
  // ... rest of code
```

## Related Code

- `add_variable` (0x401971): No duplicate check
- `get_variable` (0x4018F0): Returns first match, doesn't check for duplicates
- Variable table is a linked list, so duplicates are possible

