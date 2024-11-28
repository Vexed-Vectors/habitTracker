document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const errorMessage = document.getElementById("errorMessage");

  if (loginForm) {
    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      try {
        const response = await fetch("api/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        console.log(data)
        if (response.ok) {
          // Successful login - redirect to dashboard
          window.location.href = "/dashboard";
        } else {
          // Show error message
          errorMessage.textContent = data.error || "Login failed";
          errorMessage.style.display = "block";
        }
      } catch (error) {
        console.error("Login error:", error);
        errorMessage.textContent = "An unexpected error occurred";
        errorMessage.style.display = "block";
      }
    });
  }
});

// Function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
