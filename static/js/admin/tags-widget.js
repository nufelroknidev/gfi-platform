/**
 * Tags widget for the alternative_names admin field.
 * Reads a hidden comma-separated input, renders pill tags with remove buttons,
 * and a text input + Add button to create new tags.
 */
(function () {
  "use strict";

  function initTagsWidget(container) {
    const hidden = container.querySelector("input[type='hidden']");
    const list = container.querySelector(".tags-list");
    const input = container.querySelector(".tags-input");
    const addBtn = container.querySelector(".tags-add-btn");

    function getTags() {
      return hidden.value
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
    }

    function saveTags(tags) {
      hidden.value = tags.join(", ");
    }

    function renderTags() {
      list.innerHTML = "";
      getTags().forEach((tag) => {
        const pill = document.createElement("span");
        pill.className = "tag-pill";
        pill.textContent = tag;

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "tag-remove";
        removeBtn.setAttribute("aria-label", "Remove " + tag);
        removeBtn.textContent = "×";
        removeBtn.addEventListener("click", () => {
          saveTags(getTags().filter((t) => t !== tag));
          renderTags();
        });

        pill.appendChild(removeBtn);
        list.appendChild(pill);
      });
    }

    function addTag() {
      const val = input.value.trim();
      if (!val) return;
      const tags = getTags();
      // Split on commas so user can paste "Ascorbic acid, Vitamin C" at once
      val.split(",").forEach((t) => {
        const clean = t.trim();
        if (clean && !tags.includes(clean)) tags.push(clean);
      });
      saveTags(tags);
      renderTags();
      input.value = "";
      input.focus();
    }

    addBtn.addEventListener("click", addTag);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        addTag();
      }
    });

    renderTags();
  }

  function init() {
    document.querySelectorAll(".tags-widget").forEach(initTagsWidget);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
