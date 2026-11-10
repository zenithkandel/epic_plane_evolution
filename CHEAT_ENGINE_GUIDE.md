# Epic Plane Evolution: Definitive Cheat Engine Memory Reverse Engineering & Currency Manipulation Guide

---

## Table of Contents
1. [Architecture & The 2.14 Billion Problem](#1-architecture--the-214-billion-problem)
2. [C# BigInteger Memory Anatomy (IL2CPP WASM)](#2-c-biginteger-memory-anatomy-il2cpp-wasm)
3. [The Two States of Currency](#3-the-two-states-of-currency)
4. [Array Memory Layout in 32-bit WASM](#4-array-memory-layout-in-32-bit-wasm)
5. [The Chunk Mathematics & Formula](#5-the-chunk-mathematics--formula)
6. [Interactive Calculation Scripts (Python & JavaScript)](#6-interactive-calculation-scripts-python--javascript)
7. [Lookup Cheat Sheet (From 10B to 1 Quadrillion)](#7-lookup-cheat-sheet-from-10b-to-1-quadrillion)
8. [The "Forced Transition" Trick (Moving from Millions to Trillions)](#8-the-forced-transition-trick-moving-from-millions-to-trillions)
9. [Step-by-Step Operator Manual (With Visual Memory Dumps)](#9-step-by-step-operator-manual-with-visual-memory-dumps)
10. [Why Addresses Disappear (Immutability & Garbage Collection)](#10-why-addresses-disappear-immutability--garbage-collection)
11. [Cheat Engine Table Setup & The Freezing Strategy](#11-cheat-engine-table-setup--the-freezing-strategy)
12. [Troubleshooting & Crash Prevention](#12-troubleshooting--crash-prevention)

---

## 1. Architecture & The 2.14 Billion Problem

"Epic Plane Evolution" is built with Unity and exported via **WebGL / IL2CPP**. 

When running in Chromium browsers (Brave, Google Chrome, Edge):
* The browser runs as a **64-bit host process** (`brave.exe` / `chrome.exe`).
* The WebAssembly runtime allocates a dedicated, flat **32-bit linear memory space** within the process.
* The start of this 32-bit sandbox is the **`AllocationBase`** (e.g., `0x35400000000` or `0x28500000000`).
* All pointers inside the game's C# IL2CPP runtime are **32-bit offsets relative to `AllocationBase`**.

### Why Standard Scans Fail at 2.14 Billion:
In standard games, money is a 32-bit integer (`int32` or `uint32`), capped at $2,147,483,647$ ($2^{31}-1$). In idle and incremental games where values reach Trillions and Quadrillions, standard integers overflow.

To solve this, the developers used **`System.Numerics.BigInteger`**. Once your money passes 2.14 Billion, the game completely shifts how money is stored in RAM, breaking traditional 4-byte searches.

---

## 2. C# BigInteger Memory Anatomy (IL2CPP WASM)

In IL2CPP (32-bit WASM), the `System.Numerics.BigInteger` struct occupies exactly **8 consecutive bytes**:

```cpp
struct BigInteger {
    int32_t  _sign;   // +0x00 (4 bytes): Sign indicator or direct small value
    uint32_t _bits;   // +0x04 (4 bytes): 32-bit WASM heap pointer to uint32[] array
};
```

```
+------------------------------------+------------------------------------+
|         _sign (Bytes 0-3)          |         _bits (Bytes 4-7)          |
|              4 Bytes               |              4 Bytes               |
+------------------------------------+------------------------------------+
```

---

## 3. The Two States of Currency

### State 1: The "Small Money" State ($\le 2,147,483,647$)
* **`_sign`** contains the **literal coin amount**.
* **`_bits`** is **`NULL` (`00 00 00 00`)**. No array exists on the heap!
* **Visual Memory Dump Example (3,020,000 coins):**
  ```text
  Address      14 15 16 17  18 19 1A 1B
  ...1CC2C14   E0 14 2E 00  00 00 00 00
               \_________/  \_________/
              _sign=3020000   _bits=NULL
  ```
  *(Note: `E0 14 2E 00` in Little-Endian hex is `0x002E14E0` = `3,020,000` decimal).*

### State 2: The "BigInteger" State ($> 2,147,483,647$)
* **`_sign`** becomes **`1`** (a flag meaning positive number).
* **`_bits`** becomes a **32-bit heap pointer** pointing to an allocated `uint32[]` array.
* **Visual Memory Dump Example (Coins > 2.14B):**
  ```text
  Address      14 15 16 17  18 19 1A 1B
  ...1CC2C14   01 00 00 00  70 C5 6F 0D
               \_________/  \_________/
                _sign = 1    Pointer to Array: 0x0D6FC570
  ```
  *(Note: `70 C5 6F 0D` reversed from Little-Endian is `0x0D6FC570`).*

---

## 4. Array Memory Layout in 32-bit WASM

When `_bits` points to an array, the target memory location follows the IL2CPP Array layout:

| Offset from Array Base | Field Name | Data Type | Purpose & Details |
| :--- | :--- | :--- | :--- |
| **`+ 0x00`** | `klass` | 4 Bytes (Pointer) | IL2CPP Class metadata for `System.UInt32[]` |
| **`+ 0x04`** | `monitor` | 4 Bytes | Thread synchronization block |
| **`+ 0x08`** | `bounds` | 4 Bytes (Pointer) | Array bounds descriptor |
| **`+ 0x0C`** (`+12`) | **Array Length** | 4 Bytes (`uint32`) | Number of 32-bit chunks in the array (must be $\ge 2$) |
| **`+ 0x10`** (`+16`) | **Chunk 1 (`_bits[0]`)** | 4 Bytes (`uint32`) | Lower 32 bits ($0$ to $4,294,967,295$) |
| **`+ 0x14`** (`+20`) | **Chunk 2 (`_bits[1]`)** | 4 Bytes (`uint32`) | Multiplier for $2^{32}$ ($\approx 4.294967\text{B}$) |
| **`+ 0x18`** (`+24`) | Chunk 3 (`_bits[2]`) | 4 Bytes (`uint32`) | Multiplier for $2^{64}$ (only needed for Quintillions+) |

### Diagram of Array in Memory:
```
Array Base Address (AllocationBase + Pointer)
+------------------------+-----------------------------------------------+
| Offset                 | Content                                       |
+------------------------+-----------------------------------------------+
| +0x00 to +0x0B         | IL2CPP Header (12 bytes of internal metadata)  |
| +0x0C (Length)         | 02 00 00 00  (Length = 2 chunks)              |
| +0x10 (Chunk 1)        | Lower 32 bits of coin value                   |
| +0x14 (Chunk 2)        | Upper 32 bits (Trillion Multiplier)           |
+------------------------+-----------------------------------------------+
```

---

## 5. The Chunk Mathematics & Formula

The total coin value is mathematically reconstructed by combining the chunks in base-$2^{32}$:

$$\text{Total Coins} = \text{Chunk 1} + (\text{Chunk 2} \times 2^{32})$$
$$\text{where } 2^{32} = 4,294,967,296$$

### Step-by-Step Calculation Formula:
Given any target coin amount $\mathbf{T}$:
1. **$\text{Chunk 2} = \lfloor \mathbf{T} / 4,294,967,296 \rfloor$** *(Integer division)*
2. **$\text{Chunk 1} = \mathbf{T} \pmod{4,294,967,296}$** *(Remainder / modulo)*
3. **$\text{Array Length} = 2$**

---

## 6. Interactive Calculation Scripts (Python & JavaScript)

### Python Snippet:
Run this anywhere to get the exact numbers for any amount:
```python
def calculate_chunks(target_coins):
    CHUNK_SIZE = 4294967296  # 2^32
    chunk_2 = target_coins // CHUNK_SIZE
    chunk_1 = target_coins % CHUNK_SIZE
    
    print(f"--- TARGET: {target_coins:,} ---")
    print(f"Array Length: 2")
    print(f"Chunk 1 (Lower 32-bit): {chunk_1}")
    print(f"Chunk 2 (Multiplier):   {chunk_2}")

# Example: 50 Trillion
calculate_chunks(50_000_000_000_000)
```

### Browser Console Snippet (No Python required):
Open your browser DevTools Console (`F12`) and paste:
```javascript
function getChunks(trillions) {
    const target = BigInt(trillions) * 1000000000000n;
    const CHUNK = 4294967296n;
    console.log(`--- For ${trillions} Trillion ---`);
    console.log("Array Length: 2");
    console.log("Chunk 1:", (target % CHUNK).toString());
    console.log("Chunk 2:", (target / CHUNK).toString());
}

getChunks(50); // Calculates 50 Trillion
```

---

## 7. Lookup Cheat Sheet (From 10B to 1 Quadrillion)

| Target Amount | Display | Chunk 1 (`_bits[0]`) | Chunk 2 (`_bits[1]`) | Array Length |
| :--- | :--- | :--- | :--- | :---: |
| $10,000,000,000$ | **10B** | `1410065408` | `2` | `2` |
| $50,000,000,000$ | **50B** | `2755359744` | `11` | `2` |
| $100,000,000,000$ | **100B** | `1215752192` | `23` | `2` |
| $500,000,000,000$ | **500B** | `1783793664` | `116` | `2` |
| $1,000,000,000,000$ | **1T** | `3567587328` | `232` | `2` |
| $10,000,000,000,000$ | **10T** | `4223940608` | `2328` | `2` |
| $20,000,000,000,000$ | **20T** | `2632269824` | `4656` | `2` |
| $50,000,000,000,000$ | **50T** | `2285707264` | `11641` | `2` |
| $100,000,000,000,000$ | **100T** | `276447232` | `23283` | `2` |
| $500,000,000,000,000$ | **500T** | `1382236160` | `116415` | `2` |
| $1,000,000,000,000,000$ | **1 Quadrillion (1Q)** | `2764472320` | `232830` | `2` |

---

## 8. The "Forced Transition" Trick (Moving from Millions to Trillions)

If you currently have less than 2.14 Billion (e.g. 3 Million), the array **does not exist yet in memory** (`_bits` is `00 00 00 00`). You cannot write to an array that hasn't been allocated!

Instead of flying hundreds of times to earn 2.14B legitimately, use the **Forced Transition Trick**:

1. In Cheat Engine, find the 4-byte `MONEY VAR` (`_sign`).
2. Change its value directly to **`2140000000`** *(2.14 Billion - just under the limit)*.
3. Switch back to the game and **tap fly once** or buy a cheap level 1 upgrade.
4. Earning any coins pushes the total over $2,147,483,647$.
5. The game engine's C# code triggers:
   - It sets `_sign` to **`1`**.
   - It executes `new uint32[]` on the heap and writes the new pointer into `_bits`!
6. You are now officially in BigInteger mode, and the array is ready to edit.

---

## 9. Step-by-Step Operator Manual (With Visual Memory Dumps)

### Step 1: Attach Cheat Engine to the Correct Browser Tab
1. In Brave/Chrome, press `Shift + Esc` to open the internal Chrome Task Manager.
2. Locate the tab titled **`YT Game Wrapper WebGL`** and check its **Process ID (PID)**.
3. In Cheat Engine, click the **Monitor/Process icon** $\rightarrow$ select the matching process (e.g. `000066D0-brave.exe`).

### Step 2: Locate the `MONEY VAR` Address
1. Start with your small coin amount (e.g. `3020000`).
2. Search `Exact Value`, Type: `4 Bytes`, enter `3020000`.
3. Do one flight, scan for `Increased value` or the new number until 1 address remains.
4. Add it to your address table and label it: **`MONEY VAR (4byte)`**.

### Step 3: Trigger BigInteger Mode
*(See Section 8: Change value to `2140000000`, fly once. `MONEY VAR` will turn into `1`).*

### Step 4: Inspect Memory Viewer to Get the Pointer
1. Right-click `MONEY VAR` in Cheat Engine $\rightarrow$ click **Browse this memory region**.
2. Look at the top header of the window:
   ```text
   Protect:Read/Write  AllocationBase=35400000000  Base=35401CC2000 ...
   ```
   Note down your **`AllocationBase`** (e.g. `0x35400000000`).
3. Look at your `MONEY VAR` row:
   ```text
   address     14 15 16 17  18 19 1A 1B
   ...1CC2C14  01 00 00 00  70 C5 6F 0D
               \_________/  \_________/
                _sign = 1    Pointer bytes
   ```
4. Read the 4 bytes at `18 19 1A 1B` in **reverse order** (Little-Endian to Big-Endian):
   - `70 C5 6F 0D` $\rightarrow$ **`0x0D6FC570`**.

### Step 5: Calculate the Array Address
Add `AllocationBase` and your `Pointer`:
$$\text{Array Base} = \text{0x35400000000} + \text{0x0D6FC570} = \mathbf{\text{0x3540D6FC570}}$$

Now apply the standard offsets:
* **Array Length (`+0xC`):** `0x3540D6FC570 + 0xC` = **`3540D6FC57C`**
* **Chunk 1 (`+0x10`):** `0x3540D6FC570 + 0x10` = **`3540D6FC580`**
* **Chunk 2 (`+0x14`):** `0x3540D6FC570 + 0x14` = **`3540D6FC584`**

### Step 6: Add and Set the 3 Entries in Cheat Engine
Click **Add Address Manually** in Cheat Engine for each entry:

| Description | Address | Type | Value (for 50T) | Freeze [X] |
| :--- | :--- | :--- | :--- | :---: |
| **Array Length** | `3540D6FC57C` | 4 Bytes | **`2`** | ` ` |
| **Real money chunk 1** | `3540D6FC580` | 4 Bytes | **`2285707264`** | **`[X]`** |
| **Trillion multiplier chunk 2** | `3540D6FC584` | 4 Bytes | **`11641`** | **`[X]`** |

---

## 10. Why Addresses Disappear (Immutability & Garbage Collection)

In .NET / C#, **`BigInteger` is strictly immutable**.

Whenever an arithmetic operation happens (e.g. passive income tick, upgrade purchase, flight reward):
$$\text{coins}_{\text{new}} = \text{coins}_{\text{old}} \pm \text{delta}$$

Because the struct is immutable:
1. Unity **never modifies the existing array in place**.
2. It allocates a **brand new `uint32[]` array** elsewhere in the heap.
3. It writes the result into the new array.
4. It overwrites `_bits` with the **new array's address**.
5. The old array is orphaned and collected by the garbage collector.

**The Solution:** This is why we **Freeze (`Active [X]`)** Chunk 1 and Chunk 2 in Cheat Engine!

---

## 11. Cheat Engine Table Setup & The Freezing Strategy

### Why Freezing Works:
When you check the **`Active` [X]** box next to **Chunk 1** and **Chunk 2**:
* Cheat Engine continuously forces those exact numbers into memory many times per second.
* When the game's UI code runs to draw the money bar, it reads Chunk 1 and Chunk 2 and displays **`50T`**.
* When you buy an upgrade, the game calculates `50T - upgrade_cost`, and Cheat Engine immediately resets it back to `50T`, giving you **infinite currency**.
* Furthermore, because the value is locked, the array pointer rarely moves!

### The Perfect Final Cheat Table View:
```text
Active  Description                   Address        Type     Value
[ ]     MONEY VAR (4byte)             35401CC2C14    4 Bytes  1
[ ]     Array Length                  3540D6FC57C    4 Bytes  2
[X]     Real money chunk 1            3540D6FC580    4 Bytes  2285707264
[X]     trillion multiplier chunk 2   3540D6FC584    4 Bytes  11641
```

---

## 12. Troubleshooting & Crash Prevention

* **Why did the game crash previously?**
  * *Reason:* Modifying upgrade level variables (like `incomeLevel` or `slingshotLevel`) to arbitrary numbers like `999999` crashes the game because level data is stored in finite arrays. Requesting level index `999999` throws an `IndexOutOfRangeException` in C#.
  * *Rule:* **Only modify currency chunks**, never edit the upgrade levels directly! Buy the upgrades legitimately using your 50 Trillion coins.

* **Why did the value not update on the screen?**
  * *Reason:* Unity WebGL only re-renders the text mesh when a game event fires (a flight finishes or an upgrade button is pressed).
  * *Fix:* Simply press any upgrade button or launch your plane once; the UI will instantly refresh to your Trillions.

* **What if the browser restarts or refreshes?**
  * *Reason:* When the browser refreshes, `AllocationBase` and the memory offsets will change.
  * *Fix:* Simply repeat the 5-minute process: scan 4-byte money, apply the Forced Transition trick, read the new pointer, and set Chunk 1 and Chunk 2.
