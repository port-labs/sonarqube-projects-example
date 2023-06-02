```json showLineNumbers
{
  "identifier": "sonarqubeProject",
  "description": "This blueprint represents a SonarQube project in our software catalog",
  "title": "SonarQube Project",
  "icon": "sonarqube",
  "schema": {
    "properties": {
      "organization": {
        "type": "string",
        "title": "Organization Name"
      },
      "projectUrl": {
        "type": "string",
        "format": "url",
        "title": "Project URL"
      }
    },
    "required": []
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "relations": {}
}
```