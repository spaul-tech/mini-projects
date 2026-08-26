import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("employee_data.txt")
result = None
viewed_results = []

while True:
    print("1. Show Employee Data\n2. Department Analysis\n3. Salary Analysis\n4. Experience Analysis\n" \
        "5. Performance Analysis\n6. Generate Visualizations\n7. Exit\n\n")
    a=int(input("Enter a choice: "))
    try:
        if a==1:
            result=df
            print(result)
            viewed_results.append(result)
        elif a==2:
            print("1. Number of employees in each department.\n2. Department with the most employees.\n" \
            "3. Average salary of each department.\n4. Department with the highest average salary.\n" \
            "5. Average performance of each department.")    
            b=int(input("Enter a choice.: "))
            if b==1:
                result=df["Department"].value_counts()
                print(result)
                viewed_results.append(result)
            elif b==2:
                dc=df["Department"].value_counts()
                maximum=dc.max()
                result=dc[dc==maximum]
                print(result)
                viewed_results.append(result)
            elif b==3:
                result=df.groupby("Department")["Salary"].mean()
                print(result)
                viewed_results.append(result)
            elif b==4:
                avg=df.groupby("Department")["Salary"].mean()
                maximum=avg.max()
                result=avg[avg==maximum]
                print(result)
                viewed_results.append(result)
            elif b==5:
                result=df.groupby("Department")["Performance"].mean()
                print(result)
                viewed_results.append(result)
        elif a==3:
            print("1. Highest salary.\n2. Lowest salary.\n3. Average salary.\n" \
            "4. Top 5 highest-paid employees.\n")
            c=int(input("Enter a choice.: "))
            if c==1:
                max_sal=df["Salary"].max()
                result=df[df["Salary"]==max_sal]
                print(result)
                viewed_results.append(result)
            elif c==2:
                min_sal=df["Salary"].min()
                result=df[df["Salary"]==min_sal]
                print(result)
                viewed_results.append(result)
            elif c==3:
                result=df["Salary"].mean()
                print(result)
                viewed_results.append(result)
            elif c==4:
                top5 = df.sort_values("Salary", ascending=False).head(5)
                result=top5[["Name", "Department", "Salary"]]
                print(result)
                viewed_results.append(result)
        elif a==4:
            print("1. Employee with the most experience.\n2. Employee with the least experience.\n" \
            "3. Average experience.")
            d=int(input("Enter a choice.: "))
            if d==1:
                max_exp=df["Experience"].max()
                result=df[df["Experience"]==max_exp]
                print(result)
                viewed_results.append(result)
            elif d==2:
                min_exp=df["Experience"].min()
                result=df[df["Experience"]==min_exp]
                print(result)
                viewed_results.append(result)
            elif d==3:
                result=df["Experience"].mean()
                print(result)
                viewed_results.append(result)
        elif a==5:
            print("1. Highest-performing employee.\n2. Lowest-performing employee.\n" \
            "3. Average performance.\n4. Average performance by department.\n" \
            "5. Top 5 employees by performance.")
            e=int(input("Enter a choice.: "))
            if e==1:
                max_perf=df["Performance"].max()
                result=df[df["Performance"]==max_perf]
                print(result)
                viewed_results.append(result)
            elif e==2:
                min_perf=df["Performance"].min()
                result=df[df["Performance"]==min_perf]
                print(result)
                viewed_results.append(result)
            elif e==3:
                result=df["Performance"].mean()
                print(result)
                viewed_results.append(result)
            elif e==4:
                avg=df.groupby("Department")["Performance"].mean()
                maximum=avg.max()
                result=avg[avg==maximum]
                print(result)
                viewed_results.append(result)
            elif e==5:
                top5 = df.sort_values("Performance", ascending=False).head(5)
                result=top5[["Name", "Department", "Performance"]]
                print(result)
                viewed_results.append(result)
        elif a==6:
            print("1. Department count\n2. Salary distribution by name\n" \
            "3. Experience vs Salary\n4. Performance by department\n5. Enter manually the" \
            "column names which will give correct form of graph\n\n***Viewed graph will " \
            "automatically get saved to your device***")
            f=int(input("Enter a choice.: "))
            print("\n1.bar\n2.horizontal-bar\n3.scatter\n4.pie\n5.line-plot")
            x=int(input("Enter the graph type you want (only the number): "))
            if f==1:
                plt.figure(figsize=(8,8))
                vc=df["Department"].value_counts()
                if x == 1: plt.bar(vc.index, vc.values)
                elif x == 2: plt.barh(vc.index, vc.values)
                elif x == 3: plt.scatter(vc.index, vc.values)
                elif x == 4: plt.pie(vc.values, labels=vc.index,autopct="%1.1f%%",shadow=True)
                elif x == 5: plt.plot(vc.index, vc.values,marker=".",markersize=10,markerfacecolor="cyan")
                plt.title("Department Analysis")
                plt.savefig("department_analysis.png")
                print("Graph saved successfully")
            elif f==2:
                plt.figure(figsize=(8,8))
                if x == 1:  plt.bar(df["Name"],df["Salary"])
                elif x == 2:  plt.barh(df["Name"],df["Salary"])
                elif x == 3:  plt.scatter(df["Name"],df["Salary"])
                elif x == 4:  plt.pie(df["Salary"],labels=df["Name"],autopct="%1.1f%%",shadow=True)
                elif x == 5:  plt.plot(df["Name"],df["Salary"],marker=".",markersize=10,markerfacecolor="cyan")
                plt.title("Name VS Salary")
                plt.savefig("name_salary.png")
                print("Graph saved successfully")
            elif f==3:
                plt.figure(figsize=(8,8))
                if x==1:  plt.bar(df["Experience"],df["Salary"])
                elif x==2:  plt.barh(df["Experience"],df["Salary"])
                elif x==3:  plt.scatter(df["Experience"],df["Salary"])
                elif x==4:  plt.pie(df["Experience"],labels=df["Salary"],autopct="%1.1f%%",shadow=True)
                elif x==5:  plt.plot(df["Experience"],df["Salary"],marker=".",markersize=10,markerfacecolor="cyan")
                plt.title("Experience VS Salary")
                plt.savefig("experience_salary.png")
                print("Graph saved successfully")
            elif f==4:
                plt.figure(figsize=(8,8))
                if x==1:  plt.bar(df["Department"],df["Performance"])
                elif x==2:  plt.barh(df["Department"],df["Performance"])
                elif x==3:  plt.scatter(df["Department"],df["Performance"])
                elif x==4:  plt.pie(df["Performance"],labels=df["Department"],autopct="%1.1f%%",shadow=True)
                elif x==5:  plt.plot(df["Department"],df["Performance"],marker=".",markersize=10,markerfacecolor="cyan")
                plt.title("Department VS Performance")
                plt.savefig("dept_performance.png")
                print("Graph saved successfully")
            elif f==5:
                plt.figure(figsize=(8,8))
                print("Available columns:")
                print(df.columns.tolist())
                c1 = input("Enter the first column name: ")
                c2 = input("Enter the second column name: ")
                if x==1:  plt.bar(df[c1],df[c2])
                elif x==2:  plt.barh(df[c1],df[c2])
                elif x==3:  plt.scatter(df[c1],df[c2])
                elif x==4:  plt.pie(df[c2],labels=df[c1],autopct="%1.1f%%",shadow=True)
                elif x==5:  plt.plot(df[c1],df[c2],marker=".",markersize=10,markerfacecolor="cyan")
                plt.title(c1+" VS "+c2)
                fig=input("Use default filename? [Y/n]: ").strip().lower()
                if fig == "n" :
                    fname=input("Enter you file name: ")
                    plt.savefig(fname+".png")
                    print("Graph saved successfully")
                elif fig=="" or fig=="y":
                    plt.savefig("custom_graph.png")
                    print("Graph saved successfully")
                else:
                    print("❌ Wrong choice , file not saved")
            plt.show()
        if a >= 1 and a <= 6:
            print("\n1. Continue")
            print("2. Save viewed results")
            print("3. Exit")

            choice = int(input("Enter your choice: "))

            if choice == 2:
                if viewed_results:
                    with open("analysis_results.txt", "w") as file:
                        for result in viewed_results:
                            file.write(str(result))
                            file.write("\n" + "-" * 50 + "\n")
                    print("Viewed results exported successfully!")
                else:
                    print("No results to save.")

            elif choice == 3:
                print("Exiting program...")
                break
        elif a == 7:
            print("Exiting program...")
            break

    except ValueError:
        print("Please enter a number.")
        continue




