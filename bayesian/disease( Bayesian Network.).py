"""Estimate disease probabilities from a labeled symptom CSV.

The network has Disease as a parent of each binary symptom node (naive Bayes).
It reports posterior probabilities, not clinical diagnoses or measured accuracy.
"""

import csv
import math
import tkinter as tk
from collections import Counter, defaultdict
from pathlib import Path
from tkinter import messagebox, ttk


DATASET_PATH = Path(__file__).with_name("disease_symptoms.csv")
SMOOTHING = 1.0
UNKNOWN_VALUES = {"", "?", "unknown", "na", "n/a"}
TRUE_VALUES = {"1", "1.0", "yes", "y", "true", "present", "positive"}
FALSE_VALUES = {"0", "0.0", "no", "n", "false", "absent", "negative"}


def parse_binary(value):
	"""Parse a CSV symptom value, returning None when it is unknown."""
	value = value.strip().lower()
	if value in UNKNOWN_VALUES:
		return None
	if value in TRUE_VALUES:
		return True
	if value in FALSE_VALUES:
		return False
	raise ValueError(f"Expected a binary symptom value, got {value!r}.")


def train_network(csv_path):
	"""Estimate priors and symptom likelihoods from labeled CSV rows."""
	with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
		reader = csv.DictReader(file)
		if not reader.fieldnames:
			raise ValueError("The training CSV must have a header row.")

		headers = [header.strip() for header in reader.fieldnames]
		disease_columns = [header for header in headers if header.lower() == "disease"]
		if len(disease_columns) != 1:
			raise ValueError("The CSV must contain exactly one 'disease' column.")

		disease_column = disease_columns[0]
		symptom_columns = [header for header in headers if header != disease_column]
		if not symptom_columns:
			raise ValueError("Add one binary column per symptom to the CSV.")

		disease_counts = Counter()
		symptom_counts = defaultdict(lambda: defaultdict(lambda: [0, 0]))
		row_count = 0

		for row in reader:
			disease = (row.get(disease_column) or "").strip()
			if not disease:
				continue
			row_count += 1
			disease_counts[disease] += 1

			for symptom in symptom_columns:
				observed = parse_binary(row.get(symptom) or "")
				if observed is not None:
					counts = symptom_counts[disease][symptom]
					counts[0] += int(observed)
					counts[1] += 1

	if row_count == 0:
		raise ValueError("The CSV has no rows with a disease label.")
	if len(disease_counts) < 2:
		raise ValueError("Training data must include at least two disease labels.")

	disease_names = sorted(disease_counts)
	priors = {
		disease: (disease_counts[disease] + SMOOTHING)
		/ (row_count + SMOOTHING * len(disease_names))
		for disease in disease_names
	}
	likelihoods = {}
	for disease in disease_names:
		likelihoods[disease] = {}
		for symptom in symptom_columns:
			present_count, observed_count = symptom_counts[disease][symptom]
			likelihoods[disease][symptom] = (
				(present_count + SMOOTHING)
				/ (observed_count + 2 * SMOOTHING)
			)

	return symptom_columns, priors, likelihoods


def predict_probabilities(evidence, priors, likelihoods):
	"""Return normalized posterior probabilities for known symptom evidence."""
	log_scores = {}
	for disease, prior in priors.items():
		score = math.log(prior)
		for symptom, is_present in evidence.items():
			probability_present = likelihoods[disease][symptom]
			probability = probability_present if is_present else 1 - probability_present
			score += math.log(probability)
		log_scores[disease] = score

	max_score = max(log_scores.values())
	unnormalized = {
		disease: math.exp(score - max_score)
		for disease, score in log_scores.items()
	}
	total = sum(unnormalized.values())
	return {
		disease: probability / total
		for disease, probability in unnormalized.items()
	}


def launch_gui():
	root = tk.Tk()
	root.title("Symptom Disease Predictor")
	root.minsize(480, 440)

	try:
		symptom_columns, priors, likelihoods = train_network(DATASET_PATH)
	except (OSError, ValueError) as error:
		messagebox.showerror(
			"Unable to load training data",
			f"{error}\n\nExpected CSV: {DATASET_PATH}",
			parent=root,
		)
		root.destroy()
		return

	container = ttk.Frame(root, padding=20)
	container.pack(fill="both", expand=True)
	container.columnconfigure(0, weight=1)

	ttk.Label(
		container, text="Symptom Disease Predictor", font=("Segoe UI", 18, "bold")
	).grid(row=0, column=0, sticky="w")
	ttk.Label(
		container,
		text="Select the symptoms you are experiencing.",
	).grid(row=1, column=0, sticky="w", pady=(4, 14))

	symptoms_frame = ttk.LabelFrame(container, text="Symptoms", padding=12)
	symptoms_frame.grid(row=2, column=0, sticky="ew")
	symptom_vars = {}
	for index, symptom in enumerate(symptom_columns):
		variable = tk.BooleanVar(value=False)
		symptom_vars[symptom] = variable
		ttk.Checkbutton(
			symptoms_frame,
			text=symptom.replace("_", " "),
			variable=variable,
		).grid(row=index // 2, column=index % 2, sticky="w", padx=(0, 18), pady=4)

	result = tk.StringVar(value="Your most likely match will appear here.")

	def predict():
		evidence = {
			symptom: True
			for symptom, variable in symptom_vars.items()
			if variable.get()
		}
		if not evidence:
			messagebox.showinfo(
				"Select symptoms", "Choose at least one symptom to continue.", parent=root
			)
			return

		probabilities = predict_probabilities(evidence, priors, likelihoods)
		disease, probability = max(probabilities.items(), key=lambda item: item[1])
		result.set(f"Likely disease: {disease}\nEstimated probability: {probability:.1%}")

	ttk.Button(container, text="Predict disease", command=predict).grid(
		row=3, column=0, sticky="ew", pady=14
	)
	ttk.Label(
		container,
		textvariable=result,
		justify="left",
		font=("Segoe UI", 12, "bold"),
	).grid(row=4, column=0, sticky="w", pady=(0, 12))
	ttk.Label(
		container,
		text=" it is better to consult doctor ",
		wraplength=440,
	).grid(row=5, column=0, sticky="w")

	root.mainloop()


def main():
	launch_gui()


if __name__ == "__main__":
	main()
