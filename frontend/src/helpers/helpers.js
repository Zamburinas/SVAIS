export function login(email, password) {
    fetch("http://localhost:9001/users/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // If the response is successful, you might want to handle it here
        // For example, you can check the response status or data
        return response.json();
    })
    .then(data => {
        // Handle successful response data here if needed
        console.log(data);
    })
    .catch(error => {
        // Handle fetch errors here
        console.error('There was a problem with your fetch operation:', error);
    });
}
