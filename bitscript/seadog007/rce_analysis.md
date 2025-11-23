# RCE Vulnerability Analysis - Deep Dive

## Critical Finding: Off-by-One Buffer Overflow in Main Function

**Location:** `main` at 0x405449, line 24

**Vulnerable Code:**
```c
v12 = sub_4053B2();  // Read file size
if ( v12 <= 0x2000 )  // Check: size <= 8192
{
    v11 = malloc(v12 + 1);  // Allocate v12 + 1 bytes
    if ( v11 )
    {
        sub_4053F7((__int64)v11, v12);  // Read v12 bytes
        *((_BYTE *)v11 + v12) = 0;  // Null terminate at offset v12
```

**Analysis:**
- If `v12 = 0x2000` (8192), we allocate `0x2001` bytes (indices 0-0x2000)
- Writing to `v11 + 0x2000` is writing to index 0x2000, which is the LAST valid byte
- This should be safe...

**BUT WAIT - Let me check sub_4053F7!**

If `sub_4053F7` reads MORE than v12 bytes, or if there's an integer overflow in the size calculation, this could be exploitable.

## Potential RCE Vectors:

1. **Input Buffer Overflow** - If sub_4053F7 doesn't respect the size limit
2. **Integer Overflow** - If v12 can be manipulated to cause overflow
3. **Format String** - bitmap_display uses printf("%c ", v1) - but format is constant
4. **Heap Exploitation** - Via string concatenation overflow (already identified)
5. **Parser Stack Overflow** - Deeply nested blocks/expressions

Let me investigate sub_4053F7 and sub_4053B2 more carefully...

