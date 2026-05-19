/**
 * Specifications table widget.
 * Parses pipe-separated lines (Col1 | Col2 | Col3...) from a hidden textarea,
 * renders them as an editable table, and serializes back on change.
 */
(function () {
  "use strict";

  function parseRows(text) {
    return text
      .split("\n")
      .map((line) => line.split("|").map((c) => c.trim()))
      .filter((cols) => cols.some((c) => c.length > 0));
  }

  function serializeRows(rows) {
    return rows.map((cols) => cols.join(" | ")).join("\n");
  }

  function initSpecsWidget(container) {
    const textarea = container.querySelector("textarea.specs-hidden");
    const tableWrap = container.querySelector(".specs-table-wrap");
    const addBtn = container.querySelector(".specs-add-row");

    function getRows() {
      return parseRows(textarea.value);
    }

    function saveRows(rows) {
      textarea.value = serializeRows(rows);
    }

    function colCount(rows) {
      return rows.reduce((max, r) => Math.max(max, r.length), 2);
    }

    function renderTable() {
      const rows = getRows();
      const cols = colCount(rows);
      tableWrap.innerHTML = "";

      if (rows.length === 0) {
        tableWrap.innerHTML =
          '<p class="specs-empty">No specifications yet. Click <strong>+ Add Row</strong> to start.</p>';
        return;
      }

      const table = document.createElement("table");
      table.className = "specs-table";

      rows.forEach((row, rowIdx) => {
        const tr = document.createElement("tr");
        tr.className = rowIdx === 0 ? "specs-header-row" : "specs-data-row";

        for (let c = 0; c < cols; c++) {
          const td = document.createElement("td");
          const input = document.createElement("input");
          input.type = "text";
          input.className = "specs-cell";
          input.value = row[c] || "";
          input.addEventListener("input", () => {
            const currentRows = getRows();
            if (!currentRows[rowIdx]) currentRows[rowIdx] = [];
            currentRows[rowIdx][c] = input.value;
            saveRows(currentRows);
          });
          td.appendChild(input);
          tr.appendChild(td);
        }

        // Add column button (only on header row)
        if (rowIdx === 0) {
          const addColTd = document.createElement("td");
          addColTd.className = "specs-col-actions";
          const addColBtn = document.createElement("button");
          addColBtn.type = "button";
          addColBtn.className = "specs-btn specs-add-col-btn";
          addColBtn.title = "Add column";
          addColBtn.textContent = "+ Col";
          addColBtn.addEventListener("click", () => {
            const currentRows = getRows();
            currentRows.forEach((r) => r.push(""));
            saveRows(currentRows);
            renderTable();
          });
          addColTd.appendChild(addColBtn);
          tr.appendChild(addColTd);
        } else {
          // Remove row button
          const actionTd = document.createElement("td");
          actionTd.className = "specs-col-actions";
          const removeBtn = document.createElement("button");
          removeBtn.type = "button";
          removeBtn.className = "specs-btn specs-remove-row-btn";
          removeBtn.title = "Remove row";
          removeBtn.textContent = "×";
          removeBtn.addEventListener("click", () => {
            const currentRows = getRows();
            currentRows.splice(rowIdx, 1);
            saveRows(currentRows);
            renderTable();
          });
          actionTd.appendChild(removeBtn);
          tr.appendChild(actionTd);
        }

        table.appendChild(tr);
      });

      tableWrap.appendChild(table);
    }

    addBtn.addEventListener("click", () => {
      const rows = getRows();
      const cols = colCount(rows);
      rows.push(Array(cols).fill(""));
      saveRows(rows);
      renderTable();
      // Focus first cell of new row
      const cells = tableWrap.querySelectorAll(".specs-data-row:last-child .specs-cell");
      if (cells[0]) cells[0].focus();
    });

    renderTable();
  }

  function init() {
    document.querySelectorAll(".specs-widget").forEach(initSpecsWidget);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
