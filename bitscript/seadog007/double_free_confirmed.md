# Double Free Vulnerability - CONFIRMED

## Crash Output

```
double free or corruption (!prev)
Aborted (core dumped)
```

## What Happened

**Script execution:**
1. `string drgaAyOX = "CEAslRcADdmKsyLuNMWC";` - Creates string struct
2. `replace(drgaAyOX,3,"qNfYU");` - Modifies string (may allocate new struct)
3. `string qqqq = "DDDDDDD";` - Creates another string struct
4. `qqqq = drgaAyOX;` - **KEY LINE!** Both variables now point to SAME string struct
5. Script completes successfully
6. **During cleanup/deallocation → DOUBLE FREE!**

## Why It Crashes After Script Completion

**The crash happens during variable cleanup/deallocation:**

When the interpreter finishes executing the script, it likely:
1. Iterates through all variables
2. Frees each variable's value (if it's a string/bitmap)
3. Frees the variable entry itself

**What happens:**
1. Cleanup encounters `qqqq` → Frees the shared string struct
2. Cleanup encounters `drgaAyOX` → Tries to free the SAME string struct
3. **glibc detects double free → "double free or corruption (!prev)" → CRASH!**

## The Vulnerability Chain

### Step 1: String Assignment (Shallow Copy)

```c
// In eval_statement, case 4 (ASSIGNMENT):
qqqq = drgaAyOX;

// What happens:
1. eval_expression(drgaAyOX) → Returns pointer to drgaAyOX's string struct
2. Free qqqq's old string ("DDDDDDD")
3. qqqq.value_ptr = drgaAyOX.value_ptr  // POINTER COPY, NOT DEEP COPY!
```

**Result:** Both `qqqq` and `drgaAyOX` point to the **same string struct**!

### Step 2: Cleanup Phase

```c
// Pseudo-code for cleanup:
for (each variable in variable_table) {
    if (variable.type == STRING && variable.value_ptr) {
        free(variable.value_ptr->data);  // Free string data
        free(variable.value_ptr);        // Free string struct
    }
}
```

**When processing `qqqq`:**
- Frees the shared string struct ✅

**When processing `drgaAyOX`:**
- Tries to free the SAME string struct ❌
- **glibc detects:** "This chunk was already freed!"
- **Error:** "double free or corruption (!prev)"
- **Result:** CRASH!

## Why Previous POCs Didn't Crash

**Previous POCs (`poc_double_free.bs`, `poc_double_free_reassign.bs`):**
- They explicitly call `delete()` on both variables
- But `delete()` might have protection or the order matters
- OR the cleanup happens differently when variables are explicitly deleted

**This script:**
- No explicit `delete()` calls
- Relies on automatic cleanup at script end
- **This triggers the double free during cleanup!**

## Exploitation Potential

**Double free is a CRITICAL vulnerability:**

1. **Heap Corruption:**
   - Corrupts heap metadata (chunk headers)
   - Can lead to arbitrary write

2. **Use-After-Free:**
   - Memory used after being freed
   - Can lead to code execution

3. **Heap Exploitation Techniques:**
   - **Fastbin Attack:** Corrupt freed chunk's `fd` pointer
   - **Tcache Poisoning:** Control next allocation
   - **Unlink Attack:** Write to arbitrary address
   - **House of Spirit:** Fake chunk allocation

4. **RCE Potential:**
   - Corrupt heap → Control allocation → Write to GOT → RCE
   - Or use heap corruption to gain arbitrary write → GOT overwrite → RCE

## Severity

**CRITICAL** - This is a confirmed double free vulnerability that:
- ✅ Crashes the program (confirmed)
- ✅ Can lead to heap corruption
- ✅ Can be exploited for arbitrary write
- ✅ Can lead to Remote Code Execution (RCE)

## Next Steps for Exploitation

1. **Trigger double free during execution** (not just cleanup)
2. **Control heap layout** to make exploitation reliable
3. **Use double free to corrupt heap metadata**
4. **Gain arbitrary write primitive**
5. **Overwrite GOT entry** → RCE

This is a **critical finding** that should be exploited!

