func (c *enterpriseController) ManagerShowVehicleReports(ctx *gin.Context) {
	managerId, _ := strconv.ParseUint(ctx.Param("id"), 0, 0)
	vehicleId, _ := strconv.ParseUint(ctx.Param("vehicle_id"), 0, 0)
	if !c.authManagerVehicleUpdates(ctx, uint(vehicleId)) {
		ctx.Redirect(401, "Anauthorized")
	}

	timeNB, timeNA, err := utils.UrlQTimeStampsToUTCStrings(ctx)
	if err != nil {
		log.Println(err)
	}
	if timeNB == "" && timeNA == "" {
		data := gin.H{
			"selectdate": true,
			"managerID":  managerId,
			"vehicleID":  vehicleId,
		}
		ctx.HTML(http.StatusOK, "reports.html", data)
	} else {
		report, _ := c.ManagerGenerateReports(ctx)
		var noReports bool
		if len(report.Results) == 0 {
			noReports = true
		} else {
			noReports = false
		}
		data := gin.H{

			"selectdate": false,
			"managerID":  managerId,
			"vehicleID":  vehicleId,
			"report":     report,
			"noReports":  noReports,
		}
		ctx.HTML(http.StatusOK, "reports.html", data)
	}
}
