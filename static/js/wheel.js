// Ritu wheel + goal chip interactions. Only runs on pages that have #rituWheel.
document.addEventListener("DOMContentLoaded", () => {
  const svg = document.getElementById("rituWheel");
  if (svg) buildRituWheel(svg);

  document.querySelectorAll("#goalChips .chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll("#goalChips .chip").forEach(c => c.classList.remove("selected"));
      chip.classList.add("selected");
      const input = document.getElementById("healthGoalInput");
      if (input) input.value = chip.dataset.goal;
    });
  });
});

function buildRituWheel(svg) {
  const ritus = [
    { name: "Vasant", label: "Spring", color: "#7A9B57" },
    { name: "Grishma", label: "Summer", color: "#D9962B" },
    { name: "Varsha", label: "Monsoon", color: "#43697A" },
    { name: "Sharad", label: "Autumn", color: "#A63D2F" },
    { name: "Hemant", label: "Early Winter", color: "#8B5E34" },
    { name: "Shishir", label: "Deep Winter", color: "#2E4854" }
  ];
  const cx = 200, cy = 200, rOuter = 170, rInner = 70;

  function polar(cx, cy, r, angleDeg) {
    const a = (angleDeg - 90) * Math.PI / 180;
    return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
  }
  function describeArc(cx, cy, rOuter, rInner, startAngle, endAngle) {
    const p1 = polar(cx, cy, rOuter, endAngle);
    const p2 = polar(cx, cy, rOuter, startAngle);
    const p3 = polar(cx, cy, rInner, startAngle);
    const p4 = polar(cx, cy, rInner, endAngle);
    const large = endAngle - startAngle <= 180 ? 0 : 1;
    return `M ${p1.x} ${p1.y} A ${rOuter} ${rOuter} 0 ${large} 0 ${p2.x} ${p2.y} L ${p3.x} ${p3.y} A ${rInner} ${rInner} 0 ${large} 1 ${p4.x} ${p4.y} Z`;
  }

  const seg = 360 / ritus.length;
  ritus.forEach((r, i) => {
    const start = i * seg, end = (i + 1) * seg;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", describeArc(cx, cy, rOuter, rInner, start, end));
    path.setAttribute("fill", r.color);
    path.setAttribute("class", "ritu-seg");
    path.setAttribute("stroke", "#E7D2A4");
    path.setAttribute("stroke-width", "2");
    path.style.opacity = "0.6";
    path.addEventListener("click", () => selectRitu(r.name));
    svg.appendChild(path);

    const mid = start + seg / 2;
    const labelPos = polar(cx, cy, (rOuter + rInner) / 2, mid);
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", labelPos.x);
    text.setAttribute("y", labelPos.y);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-family", "Zilla Slab, serif");
    text.setAttribute("font-size", "12");
    text.setAttribute("font-weight", "600");
    text.setAttribute("fill", "#F4E8C8");
    text.style.pointerEvents = "none";
    text.textContent = r.name;
    svg.appendChild(text);
  });

  const hub = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  hub.setAttribute("cx", cx); hub.setAttribute("cy", cy); hub.setAttribute("r", rInner - 4);
  hub.setAttribute("fill", "#2B1B12");
  svg.appendChild(hub);

  function selectRitu(name) {
    svg.querySelectorAll(".ritu-seg").forEach(p => p.style.opacity = "0.6");
    const target = Array.from(svg.querySelectorAll(".ritu-seg")).find((p, i) => ritus[i].name === name);
    if (target) target.style.opacity = "1";
    const input = document.getElementById("rituInput");
    if (input) input.value = name;
  }
}
