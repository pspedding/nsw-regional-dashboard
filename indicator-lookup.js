const INDICATOR_LOOKUP = {
  "% Bachelor Degree": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Tourism Businesses": {
    "contentArea": "Economy",
    "frequency": "Annual",
    "dataset": "Count of Business",
    "latestPeriod": "2025-01-01"
  },
  "Median Household Income": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Population density 2024 (persons/km2)": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "Family Tax Benefit A": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  },
  "Airbnb ADR": {
    "contentArea": "Tourism",
    "frequency": "Monthly",
    "dataset": "STRA",
    "latestPeriod": "2026-05-01"
  },
  "Assault Rate (per 1,000)": {
    "contentArea": "Crime",
    "frequency": "Annual",
    "dataset": "BOCSAR",
    "latestPeriod": "2025-12-31"
  },
  "Airbnb Occupancy Rate": {
    "contentArea": "Tourism",
    "frequency": "Monthly",
    "dataset": "STRA",
    "latestPeriod": "2026-05-01"
  },
  "Number of dwellings approved": {
    "contentArea": "Housing",
    "frequency": "Monthly",
    "dataset": "Building Approvals",
    "latestPeriod": "2026-04-01"
  },
  "Natural increase in ERP": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "Median Age": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Commonwealth Rent Assistance": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  },
  "Total Businesses": {
    "contentArea": "Economy",
    "frequency": "Annual",
    "dataset": "Count of Business",
    "latestPeriod": "2025-01-01"
  },
  "JobSeeker Payment": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "JobSeeker",
    "latestPeriod": "2026-04-01"
  },
  "Total Indigenous": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Unit Price (Current)": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "Property Market",
    "latestPeriod": "2026-05-01"
  },
  "Parenting Payment Single": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  },
  "ERP Change 2023-24": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "% Under 20": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "ABS Population",
    "latestPeriod": "2021-12-31"
  },
  "Total Population": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "% ERP Change 2023-24": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "Carer Allowance": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  },
  "% Indigenous": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "% Language Other Than English": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Value of building job(s)": {
    "contentArea": "Housing",
    "frequency": "Monthly",
    "dataset": "Building Approvals",
    "latestPeriod": "2026-04-01"
  },
  "Resident Spend": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "Retail Spend",
    "latestPeriod": "2026-05-01"
  },
  "House Rent (P/W)": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "Property Market",
    "latestPeriod": "2026-05-01"
  },
  "% Over 69": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "ABS Population",
    "latestPeriod": "2021-12-31"
  },
  "Listing Visits per Property": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "Property Market",
    "latestPeriod": "2026-05-01"
  },
  "Visitor Spend": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "Retail Spend",
    "latestPeriod": "2026-05-01"
  },
  "Net internal migration": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "% Born Overseas": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Airbnb Active Listings": {
    "contentArea": "Tourism",
    "frequency": "Monthly",
    "dataset": "STRA",
    "latestPeriod": "2026-05-01"
  },
  "Airbnb  Gross Revenue": {
    "contentArea": "Tourism",
    "frequency": "Monthly",
    "dataset": "STRA",
    "latestPeriod": "2026-05-01"
  },
  "Unemployment Rate (%)": {
    "contentArea": "Economy",
    "frequency": "Quarterly",
    "dataset": "SALM",
    "latestPeriod": "2025-12-01"
  },
  "Labour Force": {
    "contentArea": "Economy",
    "frequency": "Quarterly",
    "dataset": "SALM",
    "latestPeriod": "2025-12-01"
  },
  "% Completed Year 12": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Pension Concession Card": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  },
  "Malicious Damage to Property Rate (per 1,000)": {
    "contentArea": "Crime",
    "frequency": "Annual",
    "dataset": "BOCSAR",
    "latestPeriod": "2025-12-31"
  },
  "House Price (Current)": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "Property Market",
    "latestPeriod": "2026-05-01"
  },
  "Age Pension": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  },
  "Youth Allowance (other)": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "JobSeeker",
    "latestPeriod": "2026-04-01"
  },
  "ERP at 30 June 2023": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "Drug Offences Rate (per 1,000)": {
    "contentArea": "Crime",
    "frequency": "Annual",
    "dataset": "BOCSAR",
    "latestPeriod": "2025-12-31"
  },
  "Index of Relative Socio-economic Advantage and Disadvantage": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Index of Relative Socio-economic Disadvantage": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Index of Economic Resources": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Net overseas migration": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "Manufacturing Businesses": {
    "contentArea": "Economy",
    "frequency": "Annual",
    "dataset": "Count of Business",
    "latestPeriod": "2025-01-01"
  },
  "Health Care Card": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  },
  "Index of Education and Occupation": {
    "contentArea": "Demographics",
    "frequency": "4 Yearly",
    "dataset": "ABS Census",
    "latestPeriod": "2021-06-30"
  },
  "Unit Rent (P/W)": {
    "contentArea": "Economy",
    "frequency": "Monthly",
    "dataset": "Property Market",
    "latestPeriod": "2026-05-01"
  },
  "Unemployment": {
    "contentArea": "Economy",
    "frequency": "Quarterly",
    "dataset": "SALM",
    "latestPeriod": "2025-12-01"
  },
  "Homelessness": {
    "contentArea": "Socio-Economic",
    "frequency": "Annual",
    "dataset": "Homelessness (AIHW)",
    "latestPeriod": "2025-06-30"
  },
  "Healthcare Businesses": {
    "contentArea": "Economy",
    "frequency": "Annual",
    "dataset": "Count of Business",
    "latestPeriod": "2025-01-01"
  },
  "Theft Rate (per 1,000)": {
    "contentArea": "Crime",
    "frequency": "Annual",
    "dataset": "BOCSAR",
    "latestPeriod": "2025-12-31"
  },
  "Intimidation, Stalking & Harassment Rate (per 1,000)": {
    "contentArea": "Crime",
    "frequency": "Annual",
    "dataset": "BOCSAR",
    "latestPeriod": "2025-12-31"
  },
  "ERP at 30 June 2024": {
    "contentArea": "Demographics",
    "frequency": "Annual",
    "dataset": "Regional Population",
    "latestPeriod": "2024-06-30"
  },
  "Disability Support Pension": {
    "contentArea": "Socio-Economic",
    "frequency": "Quarterly",
    "dataset": "DSS",
    "latestPeriod": "2026-03-01"
  }
};
