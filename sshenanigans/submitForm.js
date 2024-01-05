function submitForm(event) {
  event.preventDefault();

  const outputElement = document.getElementById("response_output");
  const spinnerElement = document.getElementById("wait_message");

  spinnerElement.style.display = "block";
  outputElement.style.display = "none";

  const sshPubKey = document.getElementById("ssh_pub_key_textarea").value;
  const codeParam = getQueryParam("code");
  let postUrl = "/api/create-cert";

  if (codeParam) {
    postUrl += `?code=${codeParam}`;
  }

  fetch(postUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ssh_pub_key: sshPubKey,
      principal: "admin",
    }),
  })
    .then((response) => {
      const contentType = response.headers.get("content-type");

      if (contentType && contentType.includes("application/json")) {
        return response
          .json()
          .then((data) => ({ status: response.status, body: data }));
      }

      throw new Error(`Unexpected content type: ${contentType}`);
    })
    .then((responseData) => {
      spinnerElement.style.display = "none";

      if (responseData.status >= 200 && responseData.status < 300) {
        outputElement.classList.add("success-output");
        outputElement.classList.remove("error-output");
      } else {
        outputElement.classList.add("error-output");
        outputElement.classList.remove("success-output");
      }

      outputElement.innerText = JSON.stringify(responseData.body, null, 4);
      outputElement.style.display = "block";
    })
    .catch((error) => {
      console.error("Error:", error);

      spinnerElement.style.display = "none";
      outputElement.innerText = error.toString();
      outputElement.classList.add("error-output");
      outputElement.classList.remove("success-output");
      outputElement.style.display = "block";
    });
}
