# Double Free Vulnerability Analysis

## Test Code

```bitscript
string drgaAyOX = "CEAslRcADdmKsyLuNMWC";
replace(drgaAyOX,3,"qNfYU");
string qqqq = "DDDDDDD";
qqqq = drgaAyOX;  // <-- Potential double free here!
```

## Assignment Code Analysis (case 4 in eval_statement)

**Lines 66-76:**
```c
case 4:  // ASSIGNMENT
  v9 = get_variable("qqqq");  // Get target variable
  v8 = v9;
  eval_expression(v3, drgaAyOX_ast);  // Evaluate source expression
  // v5 = pointer to drgaAyOX's string struct
  
  if ( *(_DWORD *)(v8 + 32) == 1 && *(_QWORD *)(v8 + 40) ) {  // If string and has old value
    free(*(void **)(*(_QWORD *)(v8 + 40) + 8LL));  // Free old string data
    free(*(void **)(v8 + 40));  // Free old string struct
  }
  *(_QWORD *)(v8 + 40) = v5;  // Set qqqq.value_ptr = drgaAyOX.value_ptr
```

## The Problem

**When `qqqq = drgaAyOX;` executes:**

1. **Gets qqqq variable entry** (v8)
2. **Evaluates drgaAyOX** → returns pointer to drgaAyOX's string struct (v5)
3. **Frees qqqq's old string** ("DDDDDDD"):
   - `free(qqqq.value_ptr->data)` - frees "DDDDDDD" data
   - `free(qqqq.value_ptr)` - frees "DDDDDDD" struct
4. **Sets qqqq.value_ptr = drgaAyOX.value_ptr** (v5)

**Result:** Both `qqqq` and `drgaAyOX` now point to the **same string struct**!

## Double Free Scenario

**If we then do:**
```bitscript
delete(qqqq);  // Frees the shared string struct
delete(drgaAyOX);  // Tries to free the SAME struct again → DOUBLE FREE!
```

**Or if we reassign:**
```bitscript
qqqq = "new";  // Frees the shared struct
drgaAyOX = "other";  // Tries to free the SAME struct again → DOUBLE FREE!
```

## The Vulnerability

**Issue:** String assignment doesn't create a copy - it just copies the pointer!

**When assigning:**
- `qqqq.value_ptr = drgaAyOX.value_ptr` (pointer copy, not deep copy)
- Both variables point to the same memory
- Freeing one will free the shared memory
- Freeing the other will try to free already-freed memory → **DOUBLE FREE!**

## Exploitation Potential

**Double free can lead to:**
1. **Heap corruption** - Corrupts heap metadata
2. **Use-after-free** - Memory used after being freed
3. **Arbitrary write** - If combined with heap manipulation
4. **RCE** - Through heap exploitation techniques

## Proof of Concept

```bitscript
string s1 = "first";
string s2 = "second";
s2 = s1;  // Both point to same string struct
delete(s2);  // Frees the shared struct
delete(s1);  // DOUBLE FREE! (tries to free already-freed memory)
```

This should cause a crash or heap corruption!

