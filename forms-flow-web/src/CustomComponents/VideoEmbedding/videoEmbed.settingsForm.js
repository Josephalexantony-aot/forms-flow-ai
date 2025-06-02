import baseEditForm from "@aot-technologies/formiojs/lib/components/_classes/component/Component.form";

const settingsForm = (...extend) => {
  return baseEditForm(
    [
      {
        key: "display",
        components: [
          {
            // You can ignore existing fields.
            key: "placeholder",
            ignore: true,
          },
        ],
      },
      {
        key: "data",
        components: [
          {
            // Or add your own. The syntax is form.io component definitions.
            type: "tags",
            storeas: "array",
            input: true,
            label: "Video URL",
            weight: 20,
            key: "videoEmbedding", // This will be available as component.topic
            tooltip: "Enter the video URL",
          },
        ],
      },
      {
        key: "validation",
        components: [],
      },
      {
        key: "api",
        components: [],
      },
      {
        key: "conditional",
        components: [],
      },
      {
        key: "logic",
        components: [],
      },
    ],
    ...extend
  );
};

export default settingsForm;