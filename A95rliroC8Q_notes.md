This study guide translates and condenses the comprehensive lecture on **Authentication (AuthN)** and **Authorization (AuthZ)**. It covers the transition from historical trust systems to modern distributed cryptographic protocols.

---

# **Chapter 0: Historical Context of Authentication**
### **The Evolution of Trust**
*   **Pre-Industrial Society (Implicit Trust):** Based on human recognition. Identity was verified by communal "vouching" (e.g., a village elder). Trust was contextual and local but failed to scale.
*   **Medieval Era (Physical Tokens):** Use of **Wax Seals** as signatures. This introduced the principle of **"Something you possess."** It was the first "Authentication Token," though prone to forgery (the first bypass attacks).
*   **Industrial Revolution (Shared Secrets):** Telegraph operators used **Passphrases**. This shifted the principle to **"Something you know."**
*   **Computation Era (1960s-70s):**
    *   **Project MAC (MIT):** Introduced passwords for multi-user systems.
    *   **Genesis of Hashing:** After an incident where a password file was accidentally printed in plain text, researchers developed one-way cryptographic hashing to store irreversible representations of passwords.
    *   **Public Key Infrastructure (PKI):** Diffie-Hellman (1970s) enabled two parties to create a shared secret over an untrusted medium, leading to asymmetric cryptography.
*   **Modern Era:**
    *   **MFA (Multi-Factor Authentication):** Combines Knowledge (Password), Possession (OTP/Card), and Inherence (Biometrics).
    *   **Future Trends:** **Post-Quantum Cryptography** (securing data against quantum speedups) and **Decentralized Identity** (Blockchain-based).

---

# **Chapter 1: Sessions**
### **Making the Stateless Web Stateful**
*   **The HTTP Bottleneck:** By design, HTTP is **stateless**—every request is isolated. This makes "remembering" a user’s shopping cart or login status impossible.
*   **The Session Mechanism:**
    1.  **Creation:** When a user logs in, the server generates a unique **Session ID**.
    2.  **Storage:** The server stores the Session ID and user data in a persistent store (**Redis** or a Database).
    3.  **Transmission:** The Session ID is sent to the browser via a Cookie.
    4.  **Verification:** In subsequent requests, the browser sends the Cookie; the server looks up the ID in its database to identify the user.
*   **Evolution of Storage:** Started as local files on a single server, then moved to Databases for persistence, and finally to **Distributed In-Memory Stores (Redis/Memcached)** for high-speed access in scaled environments.

---

# **Chapter 2: JWT (JSON Web Token)**
### **Self-Contained Identity**
*   **The Problem with Sessions:** In globally distributed systems, synchronizing session databases across regions introduces latency and overhead.
*   **JWT Structure (Base64 Encoded):**
    1.  **Header:** Metadata (e.g., signing algorithm like HS256).
    2.  **Payload:** Claims/Data (e.g., `sub` for UserID, `iat` for Issued At, `role`).
    3.  **Signature:** Ensures the token hasn't been tampered with. Created by signing the header + payload with a **Secret Key**.
*   **Pros:** Stateless (no DB lookup needed to verify), portable, and scalable across microservices.
*   **The Revocation Problem:** Since the server doesn't "track" JWTs, you cannot easily log a user out or revoke a token if it’s stolen.
*   **Hybrid Approach:** Use JWTs but maintain a **Blacklist** in Redis for revoked/compromised tokens.

```javascript
// Example: Signing a JWT (Node.js)
const jwt = require('jsonwebtoken');

const payload = { userId: 123, role: 'admin' };
const secret = 'super-secret-key';

// Creating a token
const token = jwt.sign(payload, secret, { expiresIn: '1h' });
console.log("Generated JWT:", token);

// Verifying a token
try {
    const decoded = jwt.verify(token, secret);
    console.log("Authenticated User:", decoded.userId);
} catch (err) {
    console.log("Invalid Token");
}
```

---

# **Chapter 3: Cookies**
### **The Transport Mechanism**
*   **Definition:** A storage mechanism in the browser that the server can "set" via HTTP headers.
*   **Security Features:**
    *   **HTTP-Only:** Prevents JavaScript from accessing the cookie (mitigates XSS).
    *   **Scope:** Cookies are only sent back to the domain that created them.
*   **Automation:** Browsers automatically attach relevant cookies to every request to the server, simplifying Auth workflows.

---

# **Chapter 4: Types of Authentication**
### **4.1 Stateful Authentication**
*   **Mechanism:** Server stores state (Session ID).
*   **Pros:** Real-time control. You can kill a session instantly.
*   **Cons:** Harder to scale; requires central storage (Redis).

### **4.2 Stateless Authentication**
*   **Mechanism:** Token (JWT) contains all the state.
*   **Pros:** Perfect for microservices; no server-side storage lookup.
*   **Cons:** Token revocation is difficult; if the secret key leaks, the system is compromised.

### **4.3 API Key Authentication**
*   **Use Case:** **Machine-to-Machine (M2M)** communication.
*   **Nature:** Usually a long-lived, cryptographically random string.
*   **Example:** Using an OpenAI API key in your server code to summarize text. No "login form" is required for the machine.

---

# **Chapter 5 & 6: OAuth 2.0 & OIDC**
### **Delegation and Identity**
*   **The Delegation Problem:** How do you give a third-party app (like a Travel App) permission to read your emails without giving them your password?
*   **OAuth 2.0 (Authorization):** A protocol to issue **Access Tokens** with limited "Scopes" (permissions).
    *   *Roles:* Resource Owner (You), Client (The App), Auth Server (Google), Resource Server (Gmail).
*   **OIDC (Authentication):** A layer on top of OAuth 2.0 that adds an **ID Token**. This allows "Sign in with Google." OAuth gives permission; OIDC gives identity.

---

# **Chapter 7 & 8: Choosing Auth & Authorization**
*   **Decision Matrix:**
    *   **Standard Web App:** Stateful (Sessions).
    *   **Distributed APIs/Mobile:** Stateless (JWT).
    *   **M2M/Integrations:** API Keys.
    *   **Social Login:** OAuth/OIDC.
*   **Authorization (RBAC):** Role-Based Access Control.
    *   Assign **Roles** (Admin, User, Editor) to users.
    *   Check roles in **Middleware** before allowing access to resources (e.g., Only an Admin can access the "Dead Zone" or deleted notes).

```javascript
// Simple RBAC Middleware Logic
const checkRole = (requiredRole) => {
    return (req, res, next) => {
        if (req.user.role !== requiredRole) {
            return res.status(403).send("Forbidden: Insufficient Permissions");
        }
        next();
    };
};

// Usage: app.get('/admin/dead-zone', authenticate, checkRole('admin'), getDeadZoneNotes);
```

---

# **Chapter 9: Error Messages and Timing Attacks**
### **Hardening the Backend**
*   **Generic Errors:** Never say "User not found" or "Incorrect password." Both confirm the existence of an account to an attacker. Use **"Invalid Credentials"** for everything.
*   **Timing Attacks:** An attacker measures how long the server takes to respond. If checking a valid username takes 10ms and an invalid one takes 2ms, they can guess valid usernames.
    *   **Solution:** Use **Constant-Time Comparison** or introduce a **Simulated Delay** so every response takes the same amount of time regardless of where it failed.

```javascript
// Defending against Timing Attacks with Simulated Delay
async function login(req, res) {
    const start = Date.now();
    const user = await findUser(req.body.email);
    
    if (user && await verifyPassword(req.body.password, user.hash)) {
        // Auth success logic
    }

    // Force a minimum response time of 500ms
    const duration = Date.now() - start;
    if (duration < 500) {
        await new Promise(resolve => setTimeout(resolve, 500 - duration));
    }
    return res.status(401).send("Authentication Failed");
}
```

---

# **New Concepts Introduced**
1.  **Post-Quantum Cryptography:** The concept of preparing for quantum computers breaking current RSA/ECC algorithms.
2.  **The "Delegation Problem":** The specific architectural challenge of sharing resources between apps without sharing passwords.
3.  **Timing Attacks:** A side-channel attack where response time leaks secret information.
4.  **OIDC vs. OAuth:** Clarifying that OAuth is for *access* and OIDC is for *identity*.
5.  **Device Code Flow:** Auth flow for input-constrained devices like Smart TVs.

---

# **Understanding Quiz**
1.  **Explain the difference between "Implicit Trust" and "Explicit Authentication" in a historical context.**
2.  **Why is HTTP's stateless nature a problem for e-commerce websites?**
3.  **What are the three components of a JWT, and what is the purpose of the signature?**
4.  **In a stateful session-based system, where is the "state" actually stored?**
5.  **Describe a "Hybrid Approach" to JWT and why it is used.**
6.  **What is an `HTTP-Only` cookie, and what specific attack does it prevent?**
7.  **Compare "Machine-to-Machine" (M2M) communication with "Human-to-Machine" communication.**
8.  **What is the "Delegation Problem," and how did sharing passwords attempt (and fail) to solve it?**
9.  **What does OIDC add to OAuth 2.0 to make it suitable for authentication?**
10. **How does a "Timing Attack" allow an attacker to guess a valid username even if the server returns a generic error?**