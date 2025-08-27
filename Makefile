compile_iotest : 

	gcc -g iotest.c -o iotest -lm 

run_iotest : 

	sudo-g5k ./iotest --mode read --nb_run 10 --nb_bloc 1 --sz_bloc 1M --filesize 256M

benchmark_taurus_HDD_RAND_READ : 

	sudo-g5k ./benchmark.sh READ RAND HDD

benchmark_taurus_HDD_SEQ_READ : 

	sudo-g5k ./benchmark.sh READ SEQ HDD

benchmark_gros_SSD_RAND_READ :

	sudo-g5k ./benchmark.sh READ RAND SSD 

benchmark_gros_SSD_SEQ_READ : 

	sudo-g5k ./benchmark.sh READ SEQ SSD



reservation_taurus_short : 

	oarsub -q default -l host=2,walltime=2:00:00 -p taurus -t monitor='wattmetre_power_watt' -I

reservation_taurus_long : 

	oarsub -q default -l host=4,walltime=12:00:00 -p taurus -t monitor='wattmetre_power_watt' -I

ior_bench_reservation_taurus : 

	oarsub -q deploy -l host=1,walltime=1:45 -p taurus 


benchmark_taurus_HDD_RAND_WRITE : 

	sudo-g5k ./benchmark.sh WRITE RAND HDD 

benchmark_taurus_HDD_SEQ_WRITE : 

	sudo-g5k ./benchmark.sh WRITE SEQ HDD 

benchmark_gros_SSD_RAND_WRITE : 

	sudo-g5k ./benchmark.sh WRITE RAND SSD 

benchmark_gros_SSD_SEQ_WRITE :

	sudo-g5k ./benchmark.sh WRITE SEQ SSD 


		



plotting_HDD_READ_RAND :

	sudo-g5k ./plotting.sh logs/HDD/READ/RAND/ baseline
	sudo-g5k ./plotting.sh logs/HDD/READ/RAND/ plot_all 
	sudo-g5k ./plotting.sh logs/HDD/READ/RAND/ box_baseline
	sudo-g5k ./plotting.sh logs/HDD/READ/RAND/ box_all 
	sudo-g5k ./plotting.sh logs/HDD/READ/RAND/ all 

plotting_HDD_READ_SEQ : 

	
	sudo-g5k ./plotting.sh logs/HDD/READ/SEQ/ baseline
	sudo-g5k ./plotting.sh logs/HDD/READ/SEQ/ plot_all 
	sudo-g5k ./plotting.sh logs/HDD/READ/SEQ/ box_baseline
	sudo-g5k ./plotting.sh logs/HDD/READ/SEQ/ box_all 
	sudo-g5k ./plotting.sh logs/HDD/READ/SEQ/ all 

	
plotting_HDD_WRITE_RAND :	
		
	

	sudo-g5k ./plotting.sh logs/HDD/WRITE/RAND/ baseline
	sudo-g5k ./plotting.sh logs/HDD/WRITE/RAND/ plot_all 
	sudo-g5k ./plotting.sh logs/HDD/WRITE/RAND/ box_baseline
	sudo-g5k ./plotting.sh logs/HDD/WRITE/RAND/ box_all 
	sudo-g5k ./plotting.sh logs/HDD/WRITE/RAND/ all 





plotting_HDD_WRITE_SEQ : 

	sudo-g5k ./plotting.sh logs/HDD/WRITE/SEQ/ baseline
	sudo-g5k ./plotting.sh logs/HDD/WRITE/SEQ/ plot_all 
	sudo-g5k ./plotting.sh logs/HDD/WRITE/SEQ/ box_baseline
	sudo-g5k ./plotting.sh logs/HDD/WRITE/SEQ/ box_all 
	sudo-g5k ./plotting.sh logs/HDD/WRITE/SEQ/ all 

	
		
format_HDD : 

	sudo-g5k ./format.sh HDD

plot_deltas_READ : 

	sudo-g5k ./plot_all_deltas.py --root logs/formatted_data/HDD/READ

plot_deltas_WRITE : 

	sudo-g5k ./plot_all_deltas.py --root logs/formatted_data/HDD/WRITE 

apply_means_READ : 

	sudo-g5k ./compute_all_means.py --root logs/formatted_data/HDD/READ --script script/maths/compute_mean.py

apply_means_WRITE : 

	sudo-g5k ./compute_all_means.py --root logs/formatted_data/HDD/WRITE --script script/maths/compute_mean.py


calcul_HDD_READ : 

	python3 script/maths/calcul_hdd.py logs/formatted_data/HDD/READ/ 


calcul_HDD_WRITE : 

	python3 script/maths/calcul_hdd.py logs/formatted_data/HDD/WRITE 
