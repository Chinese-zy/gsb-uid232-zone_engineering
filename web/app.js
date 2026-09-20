fetch("/schedule").then((res) => res.json()).then((body) => {
  document.getElementById("zone").textContent = body.zone || "";
  const list = document.getElementById("rows");
  (body.rows || []).forEach((row) => {
    const item = document.createElement("li");
    item.textContent = row.name + " " + row.at;
    list.appendChild(item);
  });
});
