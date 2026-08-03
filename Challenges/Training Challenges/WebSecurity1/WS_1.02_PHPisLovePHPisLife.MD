# WS_1.02 — PHPisLovePHPisLife

---

## Problem description

The target application consists of a web page with an input field sending a `POST` request to `/` with the parameter `code`. The input is directly concatenated into PHP code executed on the server. The target flag is stored in the `FLAG` environment variable.

---

## Recon

Submitting special characters like single quotes (`'`) or unbalanced curly braces returned a PHP syntax error (e.g., `Parse error: syntax error, unexpected ... in eval()'d code`), confirming that input is processed directly inside a server-side `eval()` block.

To execute arbitrary statements without syntax errors, the payload breaks out of the surrounding PHP logic:

```php
}; MY_PAYLOAD; if(1){

```

* `}` closes the original code block.
* `;` ends the previous statement.
* `MY_PAYLOAD` contains the custom function calls.
* `if(1){` absorbs the trailing original closing brace `}` without throwing a syntax error.

---

## Analysis

Probing the endpoint revealed a character blacklist filtering common code execution syntax:

```text
`   [   *   .   \   =

```

The absence of backticks prevents shell execution, while stripping `.` disables string concatenation.

To bypass these filters, two PHP mechanisms are used:

1. **XOR Strings:** PHP allows bitwise XOR on strings (`'A' ^ 'B'`). Any target string (like `getenv`) can be built as `('X' ^ 'Y')`, where `X` and `Y` contain only allowed characters.
2. **Variable Functions:** PHP allows calling functions dynamically from strings: `('var_dump')(...)`.

Combining both allows invoking `var_dump(getenv('FLAG'))` dynamically without writing any function name or restricted character directly:

```php
( "XOR_VAR_DUMP" ^ "KEY1" )( ( "XOR_GETENV" ^ "KEY2" )( ( "XOR_FLAG" ^ "KEY3" ) ) )

```

---

## Exploit with Insomnia

Since this vulnerability can be exploited in a single HTTP request, **Insomnia** can be used directly to craft and deliver the payload.

### Step-by-Step in Insomnia:

1. Create a new request in **Insomnia**:
* **Method:** `POST`
* **URL:** `http://phpislove.challs.cyberchallenge.it/`
* **Body type:** `Form URL Encoded`


2. Add the form parameter:
* **Name:** `code`
* **Value:** The XOR-encoded breakout string:
```php
}; (""^"00000000")((""^"000000")((""^"0000"))); if(1){
```


3. **Send** the request.
4. Inspect the **Response Body**: `var_dump()` evaluates server-side and prints the environment variable containing the flag directly inside the HTML output.

---

## Flag

```
CCIT{****************}
```

---

## What I Learned

* Bitwise XOR (`'a' ^ 'b'`) combined with variable functions (`$fn()`) provides a complete bypass against character blacklists in PHP `eval()` injections.
* Blacklisting individual characters (like `.` or `[`) is ineffective when PHP permits dynamic string construction and runtime evaluation.
* Simple single-request exploits can be executed directly within API clients like Insomnia without needing dedicated automation frameworks.