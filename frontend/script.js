const form = document.getElementById("lead-form");
const tableBody = document.getElementById("results-body");
const resultsSection = document.getElementById("results-section");
const loading = document.getElementById("loading");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!document.getElementById("consent").checked) {
    alert("Please accept the consent checkbox.");
    return;
  }

  const payload = {
    email: document.getElementById("email").value,
    credit_score: parseInt(document.getElementById("credit_score").value),
    age_group: document.getElementById("age_group").value,
    family_background: document.getElementById("family_background").value,
    income: parseInt(document.getElementById("income").value),
    comment: document.getElementById("comment").value,
  };

  loading.classList.remove("hidden");

  try {
    const res = await fetch("http://127.0.0.1:8000/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    const row = `
      <tr class="hover:bg-gray-100">
        <td class="px-4 py-2 border">${data.email}</td>
        <td class="px-4 py-2 border text-blue-600">${data.initial_score}</td>
        <td class="px-4 py-2 border text-green-600 font-semibold">${data.reranked_score}</td>
        <td class="px-4 py-2 border text-gray-700">${data.comment}</td>
      </tr>
    `;

    tableBody.insertAdjacentHTML("beforeend", row);
    resultsSection.classList.remove("hidden");

    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: "smooth" });
    }, 300);

    form.reset();
  } catch (err) {
    alert("Something went wrong: " + err.message);
  } finally {
    loading.classList.add("hidden");
  }
});
