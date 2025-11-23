# Double Free via Self-Assignment

## Location
`eval_statement` function, ASSIGNMENT case (case 4), lines 66-76

## The Vulnerability

**Code Flow for `s1 = s1;` (self-assignment):**

```c
case 4:  // ASSIGNMENT
  v9 = get_variable("s1");  // Get target variable (s1)
  v8 = v9;
  eval_expression(v3, s1_ast);  // Evaluate source (s1)
  // v5 = pointer to s1's string struct (SAME as v8 + 40!)
  
  if ( *(_DWORD *)(v8 + 32) == 1 && *(_QWORD *)(v8 + 40) ) {  // If string and has old value
    free(*(void **)(*(_QWORD *)(v8 + 40) + 8LL));  // Free old string data
    free(*(void **)(v8 + 40));  // Free old string struct
  }
  *(_QWORD *)(v8 + 40) = v5;  // Set s1.value_ptr = v5 (which is the SAME pointer!)
```

## The Problem

**When `s1 = s1;` executes:**

1. **Gets s1 variable entry** (v8)
2. **Evaluates s1** → returns pointer to s1's string struct (v5)
   - **v5 = *(v8 + 40)** (same pointer!)
3. **Frees s1's old string:**
   - `free(s1.value_ptr->data)` - frees string data
   - `free(s1.value_ptr)` - frees string struct
4. **Sets s1.value_ptr = v5** (which is the SAME pointer that was just freed!)

**Result:** 
- The string struct is **freed**
- Then `s1.value_ptr` is set to the **freed pointer**
- This creates a **use-after-free** condition
- If the freed memory is reused, accessing `s1` will read/write to wrong memory
- If cleanup tries to free `s1` again → **DOUBLE FREE!**

## Double Free Scenario

**During cleanup:**
```bitscript
string s1 = "test";
s1 = s1;  // Frees s1's string, then sets s1.value_ptr to freed pointer
// Script completes
// Cleanup tries to free s1 → Tries to free already-freed memory → DOUBLE FREE!
```

## Root Cause

**The bug:** The code doesn't check if the source and target are the same variable!

**What should happen:**
```c
if (v5 == *(_QWORD *)(v8 + 40)) {
    // Self-assignment - skip freeing!
    return;  // or just do nothing
}
```

**What actually happens:**
```c
// No check for self-assignment!
free(old_value);  // Frees the value
value_ptr = same_pointer;  // Sets to freed pointer!
```

## Exploitation Potential

**Self-assignment double free can lead to:**
1. **Use-After-Free** - Variable points to freed memory
2. **Heap Corruption** - Freed memory reused, then accessed
3. **Double Free** - Cleanup tries to free again
4. **Arbitrary Read/Write** - If combined with heap manipulation

## Proof of Concept

See `poc_double_free_self_assignment.bs`

